from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.loading import load_train_data
from src.features.text import build_text_series
from src.utils.paths import load_config, resolve_project_path


BRANCH_CONFIG_PATH = "configs/branches/m1_full_pipeline.yaml"


def build_phase3_single_model() -> Pipeline:
    """Build the best single text model from phase 3."""
    return Pipeline(
        steps=[
            (
                "vectorizer",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    binary=True,
                    strip_accents="unicode",
                ),
            ),
            (
                "classifier",
                OneVsRestClassifier(
                    LogisticRegression(
                        C=6.0,
                        max_iter=5000,
                        solver="liblinear",
                        class_weight="balanced",
                        random_state=42,
                    )
                ),
            ),
        ]
    )


def build_phase3_backup_model() -> Pipeline:
    """Build the stable backup text model used inside the phase-4 ensemble."""
    return Pipeline(
        steps=[
            (
                "vectorizer",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    min_df=2,
                    sublinear_tf=False,
                    strip_accents="unicode",
                ),
            ),
            (
                "classifier",
                OneVsRestClassifier(
                    LogisticRegression(
                        C=2.0,
                        max_iter=5000,
                        solver="liblinear",
                        class_weight="balanced",
                        random_state=42,
                    )
                ),
            ),
        ]
    )


def write_text_file(path: Path, content: str) -> None:
    """Write UTF-8 text while creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a simple markdown table without extra dependencies."""
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_lines = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, separator_line, *body_lines])


def build_oof_predictions(train_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Generate out-of-fold predictions for the phase-3 single model and phase-4 ensemble."""
    text_series = build_text_series(train_df)
    y = train_df["Label"].to_numpy()
    labels = np.sort(np.unique(y))
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    pred_single = np.empty_like(y)
    pred_ensemble = np.empty_like(y)
    fold_ids = np.empty_like(y)
    single_fold_scores: list[float] = []
    ensemble_fold_scores: list[float] = []

    for fold, (train_idx, valid_idx) in enumerate(splitter.split(text_series, y), start=1):
        single_model = build_phase3_single_model()
        backup_model = build_phase3_backup_model()

        X_train = text_series.iloc[train_idx]
        X_valid = text_series.iloc[valid_idx]
        y_train = y[train_idx]
        y_valid = y[valid_idx]

        single_model.fit(X_train, y_train)
        backup_model.fit(X_train, y_train)

        single_prob = single_model.predict_proba(X_valid)
        backup_prob = backup_model.predict_proba(X_valid)
        ensemble_prob = 0.5 * single_prob + 0.5 * backup_prob

        fold_single_pred = labels[np.argmax(single_prob, axis=1)]
        fold_ensemble_pred = labels[np.argmax(ensemble_prob, axis=1)]

        pred_single[valid_idx] = fold_single_pred
        pred_ensemble[valid_idx] = fold_ensemble_pred
        fold_ids[valid_idx] = fold

        single_fold_scores.append(f1_score(y_valid, fold_single_pred, average="macro"))
        ensemble_fold_scores.append(f1_score(y_valid, fold_ensemble_pred, average="macro"))

    analysis_df = train_df.copy()
    analysis_df["fold"] = fold_ids
    analysis_df["authors_missing"] = analysis_df["authors"].isna().astype(int)
    analysis_df["title_length"] = analysis_df["title"].fillna("").astype(str).str.len()
    analysis_df["title_word_count"] = (
        analysis_df["title"].fillna("").astype(str).str.split().map(len)
    )
    analysis_df["pred_phase3_single"] = pred_single
    analysis_df["pred_phase4_ensemble"] = pred_ensemble
    analysis_df["single_correct"] = analysis_df["Label"] == analysis_df["pred_phase3_single"]
    analysis_df["ensemble_correct"] = analysis_df["Label"] == analysis_df["pred_phase4_ensemble"]
    analysis_df["case_type"] = np.select(
        [
            analysis_df["single_correct"] & analysis_df["ensemble_correct"],
            (~analysis_df["single_correct"]) & analysis_df["ensemble_correct"],
            analysis_df["single_correct"] & (~analysis_df["ensemble_correct"]),
        ],
        ["both_correct", "fixed_by_ensemble", "hurt_by_ensemble"],
        default="both_wrong",
    )

    diagnostics = {
        "labels": labels,
        "single_fold_mean": float(np.mean(single_fold_scores)),
        "single_fold_std": float(np.std(single_fold_scores)),
        "ensemble_fold_mean": float(np.mean(ensemble_fold_scores)),
        "ensemble_fold_std": float(np.std(ensemble_fold_scores)),
        "single_oof_macro_f1": float(f1_score(y, pred_single, average="macro")),
        "ensemble_oof_macro_f1": float(f1_score(y, pred_ensemble, average="macro")),
    }
    return analysis_df, diagnostics


def per_class_metrics_df(y_true: pd.Series, y_pred: pd.Series, model_name: str) -> pd.DataFrame:
    """Return per-class precision/recall/f1 in DataFrame form."""
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    frame = pd.DataFrame(report).transpose().reset_index().rename(columns={"index": "label"})
    class_rows = frame[frame["label"].astype(str).isin([str(label) for label in sorted(y_true.unique())])].copy()
    class_rows["label"] = class_rows["label"].astype(int)
    class_rows["model_name"] = model_name
    return class_rows[["model_name", "label", "precision", "recall", "f1-score", "support"]]


def confusion_df(y_true: pd.Series, y_pred: pd.Series, labels: np.ndarray) -> pd.DataFrame:
    """Build a labeled confusion matrix DataFrame."""
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    index = [f"true_{label}" for label in labels]
    columns = [f"pred_{label}" for label in labels]
    return pd.DataFrame(matrix, index=index, columns=columns)


def top_confusions(cm_df: pd.DataFrame, labels: np.ndarray, top_k: int = 5) -> list[tuple[int, int, int]]:
    """Return the strongest off-diagonal confusion pairs."""
    matrix = cm_df.to_numpy()
    pairs: list[tuple[int, int, int]] = []
    for i, true_label in enumerate(labels):
        for j, pred_label in enumerate(labels):
            count = int(matrix[i, j])
            if i != j and count > 0:
                pairs.append((count, int(true_label), int(pred_label)))
    return sorted(pairs, reverse=True)[:top_k]


def render_error_analysis_report(
    branch_config: dict,
    analysis_df: pd.DataFrame,
    metrics_df: pd.DataFrame,
    single_cm_df: pd.DataFrame,
    ensemble_cm_df: pd.DataFrame,
    diagnostics: dict,
) -> str:
    """Render the markdown error analysis summary."""
    labels = diagnostics["labels"]
    case_counts = analysis_df["case_type"].value_counts().to_dict()
    per_label_cases = pd.crosstab(analysis_df["Label"], analysis_df["case_type"]).reindex(labels, fill_value=0)

    single_metrics = (
        metrics_df[metrics_df["model_name"] == "phase3_single"]
        .set_index("label")["f1-score"]
        .to_dict()
    )
    ensemble_metrics = (
        metrics_df[metrics_df["model_name"] == "phase4_ensemble"]
        .set_index("label")["f1-score"]
        .to_dict()
    )

    per_class_rows = []
    for label in labels:
        delta = ensemble_metrics[int(label)] - single_metrics[int(label)]
        per_class_rows.append(
            [
                str(int(label)),
                f"{single_metrics[int(label)]:.6f}",
                f"{ensemble_metrics[int(label)]:.6f}",
                f"{delta:+.6f}",
            ]
        )

    case_rows = []
    for label in labels:
        case_rows.append(
            [
                str(int(label)),
                str(int(per_label_cases.loc[label, "both_correct"]) if "both_correct" in per_label_cases.columns else 0),
                str(int(per_label_cases.loc[label, "fixed_by_ensemble"]) if "fixed_by_ensemble" in per_label_cases.columns else 0),
                str(int(per_label_cases.loc[label, "hurt_by_ensemble"]) if "hurt_by_ensemble" in per_label_cases.columns else 0),
                str(int(per_label_cases.loc[label, "both_wrong"]) if "both_wrong" in per_label_cases.columns else 0),
            ]
        )

    length_summary = (
        analysis_df.groupby("case_type")[["title_length", "title_word_count", "authors_missing"]]
        .mean()
        .round(3)
        .reset_index()
    )
    length_rows = [
        [
            row["case_type"],
            f"{row['title_length']:.3f}",
            f"{row['title_word_count']:.3f}",
            f"{row['authors_missing']:.3f}",
        ]
        for _, row in length_summary.iterrows()
    ]

    fixed_examples = analysis_df.loc[
        analysis_df["case_type"] == "fixed_by_ensemble",
        ["id", "Label", "pred_phase3_single", "pred_phase4_ensemble", "title"],
    ].head(5)
    hurt_examples = analysis_df.loc[
        analysis_df["case_type"] == "hurt_by_ensemble",
        ["id", "Label", "pred_phase3_single", "pred_phase4_ensemble", "title"],
    ].head(5)
    both_wrong_examples = analysis_df.loc[
        analysis_df["case_type"] == "both_wrong",
        ["id", "Label", "pred_phase3_single", "pred_phase4_ensemble", "title"],
    ].head(5)

    fixed_rows = [
        [
            str(int(row["id"])),
            str(int(row["Label"])),
            str(int(row["pred_phase3_single"])),
            str(int(row["pred_phase4_ensemble"])),
            row["title"][:120],
        ]
        for _, row in fixed_examples.iterrows()
    ]
    hurt_rows = [
        [
            str(int(row["id"])),
            str(int(row["Label"])),
            str(int(row["pred_phase3_single"])),
            str(int(row["pred_phase4_ensemble"])),
            row["title"][:120],
        ]
        for _, row in hurt_examples.iterrows()
    ]
    both_wrong_rows = [
        [
            str(int(row["id"])),
            str(int(row["Label"])),
            str(int(row["pred_phase3_single"])),
            str(int(row["pred_phase4_ensemble"])),
            row["title"][:120],
        ]
        for _, row in both_wrong_examples.iterrows()
    ]

    single_top_confusions = top_confusions(single_cm_df, labels)
    ensemble_top_confusions = top_confusions(ensemble_cm_df, labels)
    single_conf_rows = [[str(c), str(t), str(p)] for c, t, p in single_top_confusions]
    ensemble_conf_rows = [[str(c), str(t), str(p)] for c, t, p in ensemble_top_confusions]

    return f"""# Phase 5 Error Analysis - M1

## Models compared

- Reference single model: `exp_m1_002` (`word12_binary_c6`)
- Current winner ensemble: `exp_m1_014` (`ens_best_backup_50_50`)
- Analysis method: out-of-fold predictions on the shared `StratifiedKFold(5, shuffle=True, random_state=42)`

## Important note about metrics

- Model selection for the branch still uses **mean fold Macro F1**.
- Error analysis below uses **aggregated out-of-fold predictions** so that every training sample has one fair held-out prediction and can be inspected case-by-case.
- Vì vậy, OOF Macro F1 trong report này có thể lệch nhẹ so với mean fold CV đã ghi ở tracker.

## Fold-level selection metrics

- Phase 3 single model mean fold CV: `{diagnostics['single_fold_mean']:.6f}` with std `{diagnostics['single_fold_std']:.6f}`
- Phase 4 ensemble mean fold CV: `{diagnostics['ensemble_fold_mean']:.6f}` with std `{diagnostics['ensemble_fold_std']:.6f}`

## OOF diagnostic metrics

- Phase 3 single OOF Macro F1: `{diagnostics['single_oof_macro_f1']:.6f}`
- Phase 4 ensemble OOF Macro F1: `{diagnostics['ensemble_oof_macro_f1']:.6f}`

## Per-class F1 comparison

{markdown_table(["Label", "Single F1", "Ensemble F1", "Delta"], per_class_rows)}

## Error bucket counts

- `both_correct`: {case_counts.get('both_correct', 0)}
- `fixed_by_ensemble`: {case_counts.get('fixed_by_ensemble', 0)}
- `hurt_by_ensemble`: {case_counts.get('hurt_by_ensemble', 0)}
- `both_wrong`: {case_counts.get('both_wrong', 0)}

## Case distribution by true label

{markdown_table(["Label", "Both Correct", "Fixed by Ensemble", "Hurt by Ensemble", "Both Wrong"], case_rows)}

## Title and data-quality summary by case type

{markdown_table(["Case Type", "Avg Title Length", "Avg Title Words", "Avg Missing Authors"], length_rows)}

## Strongest confusion pairs - single model

{markdown_table(["Count", "True Label", "Pred Label"], single_conf_rows)}

## Strongest confusion pairs - ensemble

{markdown_table(["Count", "True Label", "Pred Label"], ensemble_conf_rows)}

## Representative cases fixed by ensemble

{markdown_table(["ID", "True", "Single", "Ensemble", "Title"], fixed_rows)}

## Representative cases hurt by ensemble

{markdown_table(["ID", "True", "Single", "Ensemble", "Title"], hurt_rows)}

## Representative hard cases where both are wrong

{markdown_table(["ID", "True", "Single", "Ensemble", "Title"], both_wrong_rows)}

## Main findings

- Ensemble improves the branch overall because it trades a small number of regressions for slightly more fixes and, importantly, a more stable behavior across folds.
- The clearest gains are on **Label 1** and **Label 4**. Label 1 F1 rises noticeably, and Label 4 also improves a bit.
- The main trade-off is **Label 5**, where the ensemble loses some recall/F1 compared with the single model.
- Labels **3** and **4** remain the hardest classes overall; even with the ensemble, their F1 is still much lower than Labels 1 and 5.
- The biggest persistent confusion zones are still around:
  - `1 -> 2`
  - `2 -> 1`
  - `4 -> 5`
  - `3 -> 4`
- Cases fixed by the ensemble tend to have slightly shorter titles and a higher share of missing authors, which suggests the second model is adding a different bias/decision boundary that helps on thinner-text cases.

## Recommendation for M1

- Keep `exp_m1_014` as the main candidate because it is better at the branch objective: stronger mean fold CV and lower variance.
- Keep `exp_m1_002` as the single-model fallback because it is still competitive and slightly better on some Label 5 cases.
- If another phase is run, focus on reducing confusion between:
  - Label 1 vs Label 2
  - Label 4 vs Label 5
  - Label 3 vs Label 4 / Label 5
"""


def main() -> None:
    branch_config = load_config(BRANCH_CONFIG_PATH)
    train_df = load_train_data()

    analysis_df, diagnostics = build_oof_predictions(train_df)

    metrics_df = pd.concat(
        [
            per_class_metrics_df(
                analysis_df["Label"], analysis_df["pred_phase3_single"], "phase3_single"
            ),
            per_class_metrics_df(
                analysis_df["Label"], analysis_df["pred_phase4_ensemble"], "phase4_ensemble"
            ),
        ],
        ignore_index=True,
    )

    labels = diagnostics["labels"]
    single_cm_df = confusion_df(analysis_df["Label"], analysis_df["pred_phase3_single"], labels)
    ensemble_cm_df = confusion_df(analysis_df["Label"], analysis_df["pred_phase4_ensemble"], labels)

    predictions_path = resolve_project_path("reports/battle_m1/phase5_cv_predictions.csv")
    single_cm_path = resolve_project_path("reports/battle_m1/phase5_confusion_single.csv")
    ensemble_cm_path = resolve_project_path("reports/battle_m1/phase5_confusion_ensemble.csv")
    metrics_path = resolve_project_path("reports/battle_m1/phase5_per_class_metrics.csv")
    report_path = resolve_project_path("reports/battle_m1/phase5_error_analysis.md")

    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    analysis_df.to_csv(predictions_path, index=False)
    single_cm_df.to_csv(single_cm_path)
    ensemble_cm_df.to_csv(ensemble_cm_path)
    metrics_df.to_csv(metrics_path, index=False)
    write_text_file(
        report_path,
        render_error_analysis_report(
            branch_config=branch_config,
            analysis_df=analysis_df,
            metrics_df=metrics_df,
            single_cm_df=single_cm_df,
            ensemble_cm_df=ensemble_cm_df,
            diagnostics=diagnostics,
        ),
    )

    print(f"Single OOF Macro F1: {diagnostics['single_oof_macro_f1']:.6f}")
    print(f"Ensemble OOF Macro F1: {diagnostics['ensemble_oof_macro_f1']:.6f}")
    print(f"Fixed by ensemble: {(analysis_df['case_type'] == 'fixed_by_ensemble').sum()}")
    print(f"Hurt by ensemble: {(analysis_df['case_type'] == 'hurt_by_ensemble').sum()}")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
