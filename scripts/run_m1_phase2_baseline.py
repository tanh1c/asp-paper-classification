from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.loading import load_train_and_test
from src.data.splits import build_stratified_kfold
from src.evaluation.metrics import macro_f1_scorer
from src.features.text import build_text_series
from src.utils.logging_utils import upsert_csv_row
from src.utils.paths import load_config, resolve_project_path


BRANCH_CONFIG_PATH = "configs/branches/m1_full_pipeline.yaml"


def build_m1_text_baseline(branch_config: dict) -> Pipeline:
    """Create the M1 phase-2 baseline pipeline."""
    vectorizer_config = branch_config["phase_2_plan"]["vectorizer"]
    model_config = branch_config["phase_2_plan"]["model"]

    vectorizer = TfidfVectorizer(
        analyzer=vectorizer_config["analyzer"],
        ngram_range=tuple(vectorizer_config["ngram_range"]),
        min_df=vectorizer_config["min_df"],
        max_df=vectorizer_config["max_df"],
        sublinear_tf=vectorizer_config["sublinear_tf"],
    )

    classifier = OneVsRestClassifier(
        LogisticRegression(
            C=model_config["C"],
            max_iter=model_config["max_iter"],
            solver=model_config["solver"],
            class_weight=model_config["class_weight"],
            random_state=model_config["random_state"],
        )
    )

    return Pipeline(
        steps=[
            ("tfidf", vectorizer),
            ("classifier", classifier),
        ]
    )


def write_text_file(path: Path, content: str) -> None:
    """Write a UTF-8 text file, creating the parent folder if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_quick_eda_report(train_df: pd.DataFrame, test_df: pd.DataFrame) -> str:
    """Create a lightweight markdown EDA report for branch M1."""
    missing_authors = int(train_df["authors"].isna().sum())
    duplicate_titles = int(train_df["title"].duplicated().sum())
    duplicate_dois = int(train_df["doi"].duplicated().sum())
    label_counts = train_df["Label"].value_counts().sort_index().to_dict()
    venue_counts = train_df["venue"].value_counts().to_dict()

    label_lines = "\n".join(f"- Label {label}: {count}" for label, count in label_counts.items())
    venue_lines = "\n".join(f"- {venue}: {count}" for venue, count in venue_counts.items())

    return f"""# Quick EDA - M1 Branch

## Dataset size

- Train rows: {len(train_df)}
- Test rows: {len(test_df)}
- Train columns: {", ".join(train_df.columns.tolist())}
- Test columns: {", ".join(test_df.columns.tolist())}

## Data quality checks

- Missing `authors`: {missing_authors}
- Duplicate `title` in train: {duplicate_titles}
- Duplicate `doi` in train: {duplicate_dois}

## Label distribution

{label_lines}

## Venue distribution

{venue_lines}

## Branch takeaway

- Dữ liệu còn nhỏ nên baseline text có thể là hướng mở đầu tốt nhất.
- `authors` bị thiếu nhưng không quá lớn; có thể khai thác ở phase sau nếu cần.
- `title` nhiều khả năng là nguồn tín hiệu chính của phase baseline.
"""


def render_baseline_summary(
    branch_config: dict,
    fold_scores: list[float],
    submission_path: Path,
) -> str:
    """Create a markdown summary for the phase-2 baseline run."""
    rounded_scores = [round(score, 6) for score in fold_scores]
    mean_score = round(sum(fold_scores) / len(fold_scores), 6)
    std_score = round(pd.Series(fold_scores).std(ddof=0), 6)

    return f"""# Phase 2 Baseline Summary - M1

## Branch info

- Owner: {branch_config["branch"]["owner"]}
- Branch: `{branch_config["branch"]["name"]}`
- Strategy: `{branch_config["branch"]["strategy"]}`

## Baseline selected

- Feature set: `title` only
- Vectorizer: `TF-IDF word (1,2)`
- Model: `OneVsRest Logistic Regression`
- Run ID: `{branch_config["phase_2_plan"]["run_id"]}`
- Submission ID: `{branch_config["phase_2_plan"]["submission_id"]}`

## CV result

- Fold scores: {rounded_scores}
- CV Macro F1 mean: {mean_score}
- CV std: {std_score}

## Output

- Submission file: `{submission_path.as_posix()}`

## Notes

- Benchmark nhanh trước khi khóa baseline cho thấy text-only đang ổn hơn hybrid baseline đơn giản trên stage 1.
- Đây là baseline đầu tiên của branch M1, ưu tiên tính sạch và khả năng tái chạy.
"""


def main() -> None:
    shared_config = load_config()
    branch_config = load_config(BRANCH_CONFIG_PATH)

    train_df, test_df = load_train_and_test()

    text_column = shared_config["data"]["text_column"]
    id_column = shared_config["data"]["id_column"]
    target_column = shared_config["data"]["target_column"]

    train_text = build_text_series(train_df, text_column=text_column)
    test_text = build_text_series(test_df, text_column=text_column)
    y_train = train_df[target_column]

    cv_config = shared_config["cv"]
    splitter = build_stratified_kfold(
        n_splits=cv_config["n_splits"],
        shuffle=cv_config["shuffle"],
        random_state=cv_config["random_state"],
    )

    model = build_m1_text_baseline(branch_config)
    scores = cross_val_score(model, train_text, y_train, cv=splitter, scoring=macro_f1_scorer)

    model.fit(train_text, y_train)
    test_predictions = model.predict(test_text)

    submission_path = resolve_project_path(branch_config["outputs"]["submission_file"])
    submission_path.parent.mkdir(parents=True, exist_ok=True)

    submission_frame = pd.DataFrame(
        {
            id_column: test_df[id_column],
            target_column: test_predictions,
        }
    )
    submission_frame.to_csv(submission_path, index=False)

    quick_eda_path = resolve_project_path(branch_config["outputs"]["quick_eda_report"])
    write_text_file(quick_eda_path, render_quick_eda_report(train_df, test_df))

    baseline_summary_path = resolve_project_path(branch_config["outputs"]["baseline_summary"])
    write_text_file(
        baseline_summary_path,
        render_baseline_summary(branch_config, scores.tolist(), submission_path),
    )

    mean_score = round(float(scores.mean()), 6)
    std_score = round(float(scores.std()), 6)

    tracker_row = {
        "run_id": branch_config["phase_2_plan"]["run_id"],
        "owner": branch_config["branch"]["owner"],
        "branch_name": branch_config["branch"]["name"],
        "feature_set": "title_clean_tfidf_word_1_2",
        "model": "ovr_logistic_regression",
        "cv_macro_f1": mean_score,
        "cv_std": std_score,
        "public_lb": "",
        "notes": "phase2 text-first baseline",
    }
    upsert_csv_row(
        tracker_row,
        key_field="run_id",
        tracker_path=shared_config["paths"]["experiment_tracker"],
    )

    submission_row = {
        "submission_id": branch_config["phase_2_plan"]["submission_id"],
        "owner": branch_config["branch"]["owner"],
        "branch_name": branch_config["branch"]["name"],
        "file_name": submission_path.name,
        "model_family": branch_config["phase_2_plan"]["model_family"],
        "cv_macro_f1": mean_score,
        "public_lb": "",
        "notes": "phase2 baseline generated locally",
    }
    upsert_csv_row(
        submission_row,
        key_field="submission_id",
        tracker_path=shared_config["paths"]["submission_log"],
    )

    print(f"CV mean: {mean_score}")
    print(f"CV std: {std_score}")
    print(f"Submission saved to: {submission_path}")


if __name__ == "__main__":
    main()
