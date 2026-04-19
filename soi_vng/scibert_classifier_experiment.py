from __future__ import annotations

import argparse
import importlib.util
import random
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder

from ensemble_experiment import ID_COL, LABEL_COL, RANDOM_STATE, TEST_PATH, TRAIN_PATH
from structured_text_embedding_experiment import build_structured_text


OUTPUT_DIR = Path(__file__).resolve().parent / "scibert_outputs"


def require_dependencies() -> None:
    missing = [
        name
        for name in ["torch", "transformers"]
        if importlib.util.find_spec(name) is None
    ]
    if not missing:
        return

    raise SystemExit(
        "\nMissing dependencies: "
        + ", ".join(missing)
        + "\n\nInstall them inside your current environment, then rerun:\n\n"
        "    python -m pip install torch transformers\n\n"
        "This experiment fine-tunes SciBERT directly with a sequence classification head.\n"
    )


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    import torch

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class TextDataset:
    def __init__(self, texts: list[str], labels: np.ndarray | None, tokenizer, max_length: int):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> dict:
        item = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt",
        )
        item = {key: value.squeeze(0) for key, value in item.items()}
        if self.labels is not None:
            import torch

            item["labels"] = torch.tensor(int(self.labels[idx]), dtype=torch.long)
        return item


def make_loader(dataset, batch_size: int, shuffle: bool):
    import torch

    return torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def train_one_epoch(model, loader, optimizer, scheduler, device) -> float:
    model.train()
    losses = []
    for batch in loader:
        batch = {key: value.to(device) for key, value in batch.items()}
        optimizer.zero_grad()
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        scheduler.step()
        losses.append(float(loss.detach().cpu()))
    return float(np.mean(losses)) if losses else 0.0


def predict_proba(model, loader, device) -> np.ndarray:
    import torch

    model.eval()
    probs = []
    with torch.no_grad():
        for batch in loader:
            batch = {
                key: value.to(device)
                for key, value in batch.items()
                if key != "labels"
            }
            logits = model(**batch).logits
            probs.append(torch.softmax(logits, dim=1).detach().cpu().numpy())
    return np.vstack(probs)


def build_model(model_name: str, num_labels: int):
    from transformers import AutoModelForSequenceClassification

    return AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
    )


def train_fold(
    train_texts: list[str],
    train_labels: np.ndarray,
    valid_texts: list[str],
    valid_labels: np.ndarray,
    tokenizer,
    model_name: str,
    num_labels: int,
    args,
) -> tuple[np.ndarray, float]:
    import torch
    from transformers import get_linear_schedule_with_warmup

    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    model = build_model(model_name, num_labels=num_labels).to(device)

    train_dataset = TextDataset(train_texts, train_labels, tokenizer, args.max_length)
    valid_dataset = TextDataset(valid_texts, valid_labels, tokenizer, args.max_length)
    train_loader = make_loader(train_dataset, args.batch_size, shuffle=True)
    valid_loader = make_loader(valid_dataset, args.batch_size, shuffle=False)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    total_steps = max(1, len(train_loader) * args.epochs)
    warmup_steps = int(total_steps * args.warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps,
    )

    best_score = -1.0
    best_proba = None
    patience_left = args.patience

    for epoch in range(1, args.epochs + 1):
        loss = train_one_epoch(model, train_loader, optimizer, scheduler, device)
        proba = predict_proba(model, valid_loader, device)
        pred = proba.argmax(axis=1)
        score = f1_score(valid_labels, pred, average="macro")
        print(f"    epoch={epoch} loss={loss:.5f} valid_macro_f1={score:.5f}")

        if score > best_score:
            best_score = score
            best_proba = proba
            patience_left = args.patience
        else:
            patience_left -= 1
            if patience_left <= 0:
                break

    assert best_proba is not None
    return best_proba, best_score


def run_cv(texts: list[str], labels: np.ndarray, ids: pd.Series, args):
    require_dependencies()
    set_seed(RANDOM_STATE)
    from transformers import AutoTokenizer

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    splitter = StratifiedKFold(
        n_splits=args.folds,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    oof_proba = np.zeros((len(y), len(label_encoder.classes_)), dtype=float)
    rows = []

    for fold, (train_idx, valid_idx) in enumerate(splitter.split(texts, y), start=1):
        print(f"\nFold {fold}/{args.folds}")
        train_texts = [texts[idx] for idx in train_idx]
        valid_texts = [texts[idx] for idx in valid_idx]
        proba, score = train_fold(
            train_texts,
            y[train_idx],
            valid_texts,
            y[valid_idx],
            tokenizer,
            args.model_name,
            len(label_encoder.classes_),
            args,
        )
        oof_proba[valid_idx] = proba
        rows.append({"fold": fold, "model": "scibert_sequence_classifier", "macro_f1": score})
        print(f"fold={fold} scibert_macro_f1={score:.5f}")

    oof_pred = oof_proba.argmax(axis=1)
    decoded_pred = label_encoder.inverse_transform(oof_pred)
    scores = pd.DataFrame(rows)
    oof = pd.DataFrame({ID_COL: ids, LABEL_COL: labels, "pred_label": decoded_pred})
    for pos, label in enumerate(label_encoder.classes_):
        oof[f"prob_{label}"] = oof_proba[:, pos]

    report = classification_report(labels, decoded_pred)
    cm = pd.DataFrame(
        confusion_matrix(labels, decoded_pred, labels=label_encoder.classes_),
        index=[f"true_{label}" for label in label_encoder.classes_],
        columns=[f"pred_{label}" for label in label_encoder.classes_],
    )
    cm.to_csv(OUTPUT_DIR / "confusion_matrix.csv")
    return scores, oof, report, label_encoder, tokenizer


def next_submission_path() -> Path:
    existing_numbers = []
    for path in OUTPUT_DIR.glob("submission_hieu_scibert_*.csv"):
        number = path.stem.replace("submission_hieu_scibert_", "")
        if number.isdigit():
            existing_numbers.append(int(number))
    next_number = max(existing_numbers, default=0) + 1
    return OUTPUT_DIR / f"submission_hieu_scibert_{next_number}.csv"


def fit_full_predict_test(
    train_texts: list[str],
    train_labels: np.ndarray,
    test_texts: list[str],
    test_ids: pd.Series,
    label_encoder: LabelEncoder,
    tokenizer,
    args,
) -> Path:
    import torch
    from transformers import get_linear_schedule_with_warmup

    y = label_encoder.transform(train_labels)
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    model = build_model(args.model_name, num_labels=len(label_encoder.classes_)).to(device)

    train_dataset = TextDataset(train_texts, y, tokenizer, args.max_length)
    test_dataset = TextDataset(test_texts, None, tokenizer, args.max_length)
    train_loader = make_loader(train_dataset, args.batch_size, shuffle=True)
    test_loader = make_loader(test_dataset, args.batch_size, shuffle=False)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    total_steps = max(1, len(train_loader) * args.full_epochs)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * args.warmup_ratio),
        num_training_steps=total_steps,
    )

    for epoch in range(1, args.full_epochs + 1):
        loss = train_one_epoch(model, train_loader, optimizer, scheduler, device)
        print(f"full_train_epoch={epoch} loss={loss:.5f}")

    proba = predict_proba(model, test_loader, device)
    pred = label_encoder.inverse_transform(proba.argmax(axis=1))

    submission_path = next_submission_path()
    pd.DataFrame({ID_COL: test_ids, LABEL_COL: pred}).to_csv(submission_path, index=False)

    probabilities = pd.DataFrame({ID_COL: test_ids, "pred_label": pred})
    for pos, label in enumerate(label_encoder.classes_):
        probabilities[f"prob_{label}"] = proba[:, pos]
    probabilities.to_csv(OUTPUT_DIR / "test_probabilities.csv", index=False)
    return submission_path


def write_summary(scores, report, args, submission_path: Path | None) -> None:
    lines = [
        "# SciBERT Classifier Experiment",
        "",
        "## Goal",
        "",
        "Fine-tune SciBERT directly as a sequence classifier on structured text without authors.",
        "",
        "## Structured Text",
        "",
        "```text",
        "title: <clean_title> [SEP] venue: <clean_venue> [SEP] year: <year> [SEP] doi publisher: <doi_prefix> [SEP] doi source: <doi_suffix_head_or_none>",
        "```",
        "",
        "## Model",
        "",
        f"- Model: `{args.model_name}`",
        f"- Epochs per fold: `{args.epochs}`",
        f"- Full-train epochs: `{args.full_epochs}`",
        f"- Learning rate: `{args.learning_rate}`",
        f"- Weight decay: `{args.weight_decay}`",
        f"- Batch size: `{args.batch_size}`",
        f"- Max length: `{args.max_length}`",
        "",
        "## CV Scores",
        "",
        "```text",
        scores.to_string(index=False),
        "",
        f"mean_macro_f1 = {scores['macro_f1'].mean():.6f}",
        f"std_macro_f1  = {scores['macro_f1'].std():.6f}",
        "```",
        "",
        "## Classification Report",
        "",
        "```text",
        report,
        "```",
        "",
        "## Output Files",
        "",
        "- `structured_text_train.csv`",
        "- `structured_text_test.csv`",
        "- `cv_scores.csv`",
        "- `oof_predictions.csv`",
        "- `confusion_matrix.csv`",
        "- `test_probabilities.csv`",
    ]
    if submission_path is not None:
        lines.append(f"- `{submission_path.name}`")

    (OUTPUT_DIR / "experiment_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="allenai/scibert_scivocab_uncased")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--full-epochs", type=int, default=4)
    parser.add_argument("--patience", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--max-length", type=int, default=160)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--warmup-ratio", type=float, default=0.1)
    parser.add_argument("--skip-test", action="store_true")
    parser.add_argument("--cpu", action="store_true")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    train_df = pd.read_csv(TRAIN_PATH)
    train_text = build_structured_text(train_df)
    structured_train = train_df[[ID_COL, LABEL_COL]].copy()
    structured_train["structured_text"] = train_text
    structured_train.to_csv(OUTPUT_DIR / "structured_text_train.csv", index=False)

    print("Structured text preview:")
    print(structured_train.head(5).to_string(index=False))

    scores, oof, report, label_encoder, tokenizer = run_cv(
        train_text.tolist(),
        train_df[LABEL_COL].to_numpy(),
        train_df[ID_COL],
        args,
    )
    scores.to_csv(OUTPUT_DIR / "cv_scores.csv", index=False)
    oof.to_csv(OUTPUT_DIR / "oof_predictions.csv", index=False)

    submission_path = None
    if not args.skip_test and TEST_PATH.exists():
        test_df = pd.read_csv(TEST_PATH)
        test_text = build_structured_text(test_df)
        structured_test = test_df[[ID_COL]].copy()
        structured_test["structured_text"] = test_text
        structured_test.to_csv(OUTPUT_DIR / "structured_text_test.csv", index=False)
        submission_path = fit_full_predict_test(
            train_text.tolist(),
            train_df[LABEL_COL].to_numpy(),
            test_text.tolist(),
            test_df[ID_COL],
            label_encoder,
            tokenizer,
            args,
        )

    write_summary(scores, report, args, submission_path)
    print("\nMean CV score:")
    print(scores["macro_f1"].mean())
    print(f"\nOutputs written to: {OUTPUT_DIR}")
    if submission_path is not None:
        print(f"Submission: {submission_path}")


if __name__ == "__main__":
    main()
