from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler

from ensemble_experiment import (
    ID_COL,
    LABEL_COL,
    RANDOM_STATE,
    TEST_PATH,
    clean_text,
    doi_prefix,
    doi_suffix_head,
)


OUTPUT_DIR = Path(__file__).resolve().parent / "structured_embedding_outputs"
TRAIN_WITH_ABSTRACT_PATH = (
    Path(__file__).resolve().parent / "Stage_1_publcitrain_with_abstract_only (1).csv"
)
ABSTRACT_COL = "abstract"


def require_sentence_transformers() -> None:
    if importlib.util.find_spec("sentence_transformers") is not None:
        return

    raise SystemExit(
        "\nMissing dependency: sentence-transformers\n\n"
        "Install it inside your current environment, then rerun:\n\n"
        "    python -m pip install sentence-transformers\n\n"
        "This script uses a frozen pretrained NLP embedding model, then trains a "
        "small classifier on top.\n"
    )


def normalize_year(value: object) -> str:
    if pd.isna(value):
        return "missing"
    text = str(value).strip()
    return text if text else "missing"


def normalize_doi_source(value: object) -> str:
    source = doi_suffix_head(value)
    return source if source else "none"


def build_structured_text(df: pd.DataFrame) -> pd.Series:
    title = df["title"].map(clean_text)
    venue = df["venue"].map(clean_text).replace("", "missing")
    year = df["year"].map(normalize_year)
    prefix = df["doi"].map(doi_prefix)
    source = df["doi"].map(normalize_doi_source)

    return (
        "title: "
        + title
        + " [SEP] venue: "
        + venue
        + " [SEP] year: "
        + year
        + " [SEP] doi publisher: "
        + prefix
        + " [SEP] doi source: "
        + source
    )


def load_train_data() -> tuple[pd.DataFrame, int]:
    train_df = pd.read_csv(TRAIN_WITH_ABSTRACT_PATH)
    if ABSTRACT_COL not in train_df.columns:
        raise ValueError(f"Missing required column: {ABSTRACT_COL}")

    rows_before = len(train_df)
    train_df = train_df.dropna(subset=[ABSTRACT_COL]).copy()
    dropped_rows = rows_before - len(train_df)
    return train_df, dropped_rows


def encode_texts(texts: list[str], model_name: str, batch_size: int) -> np.ndarray:
    require_sentence_transformers()
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings.astype(np.float32)


def make_classifier(c: float) -> LogisticRegression:
    return LogisticRegression(
        C=c,
        max_iter=3000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )


def next_submission_path() -> Path:
    existing_numbers = []
    for path in OUTPUT_DIR.glob("submission_hieu_embedding_*.csv"):
        number = path.stem.replace("submission_hieu_embedding_", "")
        if number.isdigit():
            existing_numbers.append(int(number))

    next_number = max(existing_numbers, default=0) + 1
    return OUTPUT_DIR / f"submission_hieu_embedding_{next_number}.csv"


def run_cv(
    embeddings: np.ndarray,
    labels: np.ndarray,
    ids: pd.Series,
    n_splits: int,
    c: float,
) -> tuple[pd.DataFrame, pd.DataFrame, str, LabelEncoder, StandardScaler]:
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)
    classes = np.arange(len(label_encoder.classes_))

    splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    oof_proba = np.zeros((len(y), len(classes)), dtype=float)
    oof_pred = np.zeros(len(y), dtype=int)
    rows = []

    for fold, (train_idx, valid_idx) in enumerate(splitter.split(embeddings, y), start=1):
        scaler = StandardScaler()
        x_train = scaler.fit_transform(embeddings[train_idx])
        x_valid = scaler.transform(embeddings[valid_idx])

        model = make_classifier(c)
        model.fit(x_train, y[train_idx])

        proba = model.predict_proba(x_valid)
        pred = proba.argmax(axis=1)

        oof_proba[valid_idx] = proba
        oof_pred[valid_idx] = pred
        score = f1_score(y[valid_idx], pred, average="macro")
        rows.append({"fold": fold, "model": "structured_embedding_logistic", "macro_f1": score})
        print(f"fold={fold} structured_embedding_macro_f1={score:.5f}")

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

    full_scaler = StandardScaler()
    full_scaler.fit(embeddings)
    return scores, oof, report, label_encoder, full_scaler


def fit_full_and_predict(
    train_embeddings: np.ndarray,
    labels: np.ndarray,
    test_embeddings: np.ndarray,
    test_ids: pd.Series,
    label_encoder: LabelEncoder,
    scaler: StandardScaler,
    c: float,
) -> Path:
    y = label_encoder.transform(labels)
    x_train = scaler.transform(train_embeddings)
    x_test = scaler.transform(test_embeddings)

    model = make_classifier(c)
    model.fit(x_train, y)
    pred = label_encoder.inverse_transform(model.predict(x_test))
    proba = model.predict_proba(x_test)

    submission_path = next_submission_path()
    pd.DataFrame({ID_COL: test_ids, LABEL_COL: pred}).to_csv(submission_path, index=False)

    probabilities = pd.DataFrame({ID_COL: test_ids, "pred_label": pred})
    for pos, label in enumerate(label_encoder.classes_):
        probabilities[f"prob_{label}"] = proba[:, pos]
    probabilities.to_csv(OUTPUT_DIR / "test_probabilities.csv", index=False)

    return submission_path


def write_summary(
    scores: pd.DataFrame,
    report: str,
    model_name: str,
    c: float,
    train_path: Path,
    train_rows: int,
    dropped_abstract_rows: int,
    submission_path: Path | None,
) -> None:
    mean_score = scores["macro_f1"].mean()
    std_score = scores["macro_f1"].std()
    lines = [
        "# Structured Text Embedding Experiment",
        "",
        "## Goal",
        "",
        "Classify papers by converting selected fields into one structured text input, excluding authors.",
        "",
        "## Data",
        "",
        f"- Train file: `{train_path.as_posix()}`",
        f"- Train rows after dropping NaN abstracts: `{train_rows}`",
        f"- Dropped rows with NaN abstract: `{dropped_abstract_rows}`",
        "",
        "## Structured Text Format",
        "",
        "```text",
        "title: <clean_title> [SEP] venue: <clean_venue> [SEP] year: <year> [SEP] doi publisher: <doi_prefix> [SEP] doi source: <doi_suffix_head_or_none>",
        "```",
        "",
        "## Model",
        "",
        f"- Embedding model: `{model_name}`",
        "- Embedding mode: frozen pretrained encoder",
        f"- Classifier: `LogisticRegression(C={c}, class_weight='balanced')`",
        "- Authors: excluded from model input",
        "",
        "## CV Result",
        "",
        "```text",
        scores.to_string(index=False),
        "",
        f"mean_macro_f1 = {mean_score:.6f}",
        f"std_macro_f1  = {std_score:.6f}",
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
        "- `structured_text_train.csv`: structured text used for train rows.",
        "- `structured_text_test.csv`: structured text used for test rows.",
        "- `cv_scores.csv`: fold-level scores.",
        "- `oof_predictions.csv`: OOF predictions and probabilities.",
        "- `confusion_matrix.csv`: OOF confusion matrix.",
        "- `test_probabilities.csv`: test probabilities.",
    ]
    if submission_path is not None:
        lines.append(f"- `{submission_path.name}`: numbered submission from the full-train model.")

    (OUTPUT_DIR / "experiment_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-name",
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="SentenceTransformer model name.",
    )
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--c", type=float, default=1.0)
    parser.add_argument(
        "--skip-test",
        action="store_true",
        help="Only run CV; do not create a test submission.",
    )
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_df, dropped_abstract_rows = load_train_data()
    print(
        f"Loaded train data from {TRAIN_WITH_ABSTRACT_PATH.name}: "
        f"{len(train_df)} rows after dropping {dropped_abstract_rows} rows with NaN abstract."
    )

    train_text = build_structured_text(train_df)
    train_text_frame = train_df[[ID_COL, LABEL_COL]].copy()
    train_text_frame["structured_text"] = train_text
    train_text_frame.to_csv(OUTPUT_DIR / "structured_text_train.csv", index=False)

    print("Structured text preview:")
    print(train_text_frame.head(5).to_string(index=False))

    train_embeddings = encode_texts(
        train_text.tolist(),
        model_name=args.model_name,
        batch_size=args.batch_size,
    )
    np.save(OUTPUT_DIR / "train_embeddings.npy", train_embeddings)

    scores, oof, report, label_encoder, scaler = run_cv(
        train_embeddings,
        labels=train_df[LABEL_COL].to_numpy(),
        ids=train_df[ID_COL],
        n_splits=args.folds,
        c=args.c,
    )
    scores.to_csv(OUTPUT_DIR / "cv_scores.csv", index=False)
    oof.to_csv(OUTPUT_DIR / "oof_predictions.csv", index=False)

    submission_path = None
    if not args.skip_test and TEST_PATH.exists():
        test_df = pd.read_csv(TEST_PATH)
        test_text = build_structured_text(test_df)
        test_text_frame = test_df[[ID_COL]].copy()
        test_text_frame["structured_text"] = test_text
        test_text_frame.to_csv(OUTPUT_DIR / "structured_text_test.csv", index=False)

        test_embeddings = encode_texts(
            test_text.tolist(),
            model_name=args.model_name,
            batch_size=args.batch_size,
        )
        np.save(OUTPUT_DIR / "test_embeddings.npy", test_embeddings)
        submission_path = fit_full_and_predict(
            train_embeddings,
            labels=train_df[LABEL_COL].to_numpy(),
            test_embeddings=test_embeddings,
            test_ids=test_df[ID_COL],
            label_encoder=label_encoder,
            scaler=scaler,
            c=args.c,
        )

    write_summary(
        scores,
        report,
        args.model_name,
        args.c,
        TRAIN_WITH_ABSTRACT_PATH,
        len(train_df),
        dropped_abstract_rows,
        submission_path,
    )

    print("\nMean CV score:")
    print(scores["macro_f1"].mean())
    print(f"\nOutputs written to: {OUTPUT_DIR}")
    if submission_path is not None:
        print(f"Submission: {submission_path}")


if __name__ == "__main__":
    main()
