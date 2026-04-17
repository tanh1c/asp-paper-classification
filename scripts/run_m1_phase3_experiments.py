from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_predict, cross_val_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.svm import LinearSVC

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.loading import load_train_and_test
from src.data.splits import build_stratified_kfold
from src.features.metadata import build_metadata_features
from src.features.text import build_text_series
from src.utils.logging_utils import upsert_csv_row
from src.utils.paths import load_config, resolve_project_path


BRANCH_CONFIG_PATH = "configs/branches/m1_full_pipeline.yaml"
PHASE2_BASELINE_RUN_ID = "exp_m1_001"


@dataclass(frozen=True)
class CandidateSpec:
    run_id: str
    name: str
    direction: str
    feature_set: str
    model_name: str
    input_key: str


def write_text_file(path: Path, content: str) -> None:
    """Write a UTF-8 text file, creating parents when needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_phase3_inputs(train_df: pd.DataFrame, test_df: pd.DataFrame) -> dict[str, pd.DataFrame | pd.Series]:
    """Prepare reusable feature views for phase-3 candidates."""
    train_base = train_df.copy()
    test_base = test_df.copy()

    train_base["title_clean"] = build_text_series(train_base)
    test_base["title_clean"] = build_text_series(test_base)

    for frame in [train_base, test_base]:
        frame["venue_tok"] = "venue_" + frame["venue"].fillna("missing").astype(str).str.lower()
        frame["year_bucket"] = pd.cut(
            frame["year"],
            bins=[0, 2010, 2015, 2020, 2030],
            labels=["y_pre2010", "y_2011_2015", "y_2016_2020", "y_2021_2030"],
            include_lowest=True,
        ).astype(str)
        frame["title_plus_venue"] = frame["title_clean"] + " " + frame["venue_tok"]
        frame["title_plus_venue_year"] = (
            frame["title_clean"] + " " + frame["venue_tok"] + " " + frame["year_bucket"]
        )

    train_meta = build_metadata_features(train_df)
    test_meta = build_metadata_features(test_df)
    train_meta["title_clean"] = build_text_series(train_meta)
    test_meta["title_clean"] = build_text_series(test_meta)

    hybrid_columns = [
        "title_clean",
        "venue_clean",
        "doi_prefix",
        "year",
        "year_missing",
        "author_count",
        "doi_length",
        "title_length",
        "title_word_count",
    ]

    return {
        "title_clean": train_base["title_clean"],
        "title_plus_venue": train_base["title_plus_venue"],
        "title_plus_venue_year": train_base["title_plus_venue_year"],
        "hybrid_sparse": train_meta[hybrid_columns],
        "test_title_clean": test_base["title_clean"],
        "test_title_plus_venue": test_base["title_plus_venue"],
        "test_title_plus_venue_year": test_base["title_plus_venue_year"],
        "test_hybrid_sparse": test_meta[hybrid_columns],
    }


def build_candidate_model(name: str) -> Pipeline:
    """Return the configured phase-3 candidate pipeline."""
    if name == "word12_binary_c6":
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

    if name == "word12_binary_c4":
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
                            C=4.0,
                            max_iter=5000,
                            solver="liblinear",
                            class_weight="balanced",
                            random_state=42,
                        )
                    ),
                ),
            ]
        )

    if name == "word12_binary_c8":
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
                            C=8.0,
                            max_iter=5000,
                            solver="liblinear",
                            class_weight="balanced",
                            random_state=42,
                        )
                    ),
                ),
            ]
        )

    if name == "word13_binary_c6":
        return Pipeline(
            steps=[
                (
                    "vectorizer",
                    TfidfVectorizer(
                        analyzer="word",
                        ngram_range=(1, 3),
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

    if name == "title_venue_binary_c6":
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

    if name == "hybrid_word13_venue_lr":
        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "text",
                    TfidfVectorizer(
                        analyzer="word",
                        ngram_range=(1, 3),
                        sublinear_tf=True,
                    ),
                    "title_clean",
                ),
                ("venue", OneHotEncoder(handle_unknown="ignore"), ["venue_clean"]),
                (
                    "num",
                    Pipeline([("imputer", SimpleImputer(strategy="median"))]),
                    ["year", "year_missing", "author_count", "title_length", "title_word_count"],
                ),
            ],
            remainder="drop",
            sparse_threshold=1.0,
        )
        return Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (
                    "classifier",
                    OneVsRestClassifier(
                        LogisticRegression(
                            C=4.0,
                            max_iter=5000,
                            solver="liblinear",
                            class_weight="balanced",
                            random_state=42,
                        )
                    ),
                ),
            ]
        )

    if name == "word12_svm_none_c05":
        return Pipeline(
            steps=[
                (
                    "vectorizer",
                    TfidfVectorizer(
                        analyzer="word",
                        ngram_range=(1, 2),
                        sublinear_tf=True,
                    ),
                ),
                (
                    "classifier",
                    LinearSVC(
                        C=0.5,
                        class_weight=None,
                        random_state=42,
                        max_iter=10000,
                    ),
                ),
            ]
        )

    if name == "word13_ridge":
        return Pipeline(
            steps=[
                (
                    "vectorizer",
                    TfidfVectorizer(
                        analyzer="word",
                        ngram_range=(1, 3),
                        sublinear_tf=True,
                    ),
                ),
                ("classifier", RidgeClassifier(alpha=1.0)),
            ]
        )

    if name == "char46_lr_c4":
        return Pipeline(
            steps=[
                (
                    "vectorizer",
                    TfidfVectorizer(
                        analyzer="char_wb",
                        ngram_range=(4, 6),
                        sublinear_tf=True,
                    ),
                ),
                (
                    "classifier",
                    OneVsRestClassifier(
                        LogisticRegression(
                            C=4.0,
                            max_iter=5000,
                            solver="liblinear",
                            class_weight="balanced",
                            random_state=42,
                        )
                    ),
                ),
            ]
        )

    if name == "word12_tfidf_c2_min2":
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

    raise ValueError(f"Unknown candidate model '{name}'.")


def build_phase3_candidate_specs() -> list[CandidateSpec]:
    """Curated candidates that represent different phase-3 directions."""
    return [
        CandidateSpec(
            run_id="exp_m1_002",
            name="word12_binary_c6",
            direction="text_tuned_binary",
            feature_set="title_clean_word12_binary",
            model_name="ovr_logistic_regression",
            input_key="title_clean",
        ),
        CandidateSpec(
            run_id="exp_m1_003",
            name="word12_binary_c4",
            direction="text_tuned_binary",
            feature_set="title_clean_word12_binary",
            model_name="ovr_logistic_regression",
            input_key="title_clean",
        ),
        CandidateSpec(
            run_id="exp_m1_004",
            name="word12_binary_c8",
            direction="text_tuned_binary",
            feature_set="title_clean_word12_binary",
            model_name="ovr_logistic_regression",
            input_key="title_clean",
        ),
        CandidateSpec(
            run_id="exp_m1_005",
            name="word13_binary_c6",
            direction="text_trigram",
            feature_set="title_clean_word13_binary",
            model_name="ovr_logistic_regression",
            input_key="title_clean",
        ),
        CandidateSpec(
            run_id="exp_m1_006",
            name="title_venue_binary_c6",
            direction="text_plus_metadata_tokens",
            feature_set="title_plus_venue_word12_binary",
            model_name="ovr_logistic_regression",
            input_key="title_plus_venue",
        ),
        CandidateSpec(
            run_id="exp_m1_007",
            name="hybrid_word13_venue_lr",
            direction="hybrid_sparse",
            feature_set="title_word13_plus_venue_numeric",
            model_name="ovr_logistic_regression",
            input_key="hybrid_sparse",
        ),
        CandidateSpec(
            run_id="exp_m1_008",
            name="word12_svm_none_c05",
            direction="linear_svm",
            feature_set="title_clean_word12_tfidf",
            model_name="linear_svc",
            input_key="title_clean",
        ),
        CandidateSpec(
            run_id="exp_m1_009",
            name="word13_ridge",
            direction="ridge_text",
            feature_set="title_clean_word13_tfidf",
            model_name="ridge_classifier",
            input_key="title_clean",
        ),
        CandidateSpec(
            run_id="exp_m1_010",
            name="char46_lr_c4",
            direction="char_model",
            feature_set="title_clean_char46_tfidf",
            model_name="ovr_logistic_regression",
            input_key="title_clean",
        ),
        CandidateSpec(
            run_id="exp_m1_011",
            name="word12_tfidf_c2_min2",
            direction="text_stability_backup",
            feature_set="title_clean_word12_tfidf_min2",
            model_name="ovr_logistic_regression",
            input_key="title_clean",
        ),
    ]


def render_phase3_summary(
    branch_config: dict,
    baseline_mean: float,
    results_df: pd.DataFrame,
    best_result: pd.Series,
    submission_path: Path,
) -> str:
    """Create a readable markdown summary for the phase-3 experiments."""
    table_rows = []
    for _, row in results_df.iterrows():
        table_rows.append(
            f"| {row['run_id']} | {row['candidate_name']} | {row['direction']} | {row['cv_macro_f1']:.6f} | {row['cv_std']:.6f} |"
        )
    table_md = "\n".join(table_rows)
    improvement = best_result["cv_macro_f1"] - baseline_mean

    return f"""# Phase 3 Experiment Summary - M1

## Branch info

- Owner: {branch_config["branch"]["owner"]}
- Branch: `{branch_config["branch"]["name"]}`
- Strategy at start of phase: `{branch_config["branch"]["strategy"]}`

## Goal of this phase

- thử nhiều hướng một cách công bằng trên cùng CV
- xác định hướng nào thực sự tốt hơn baseline Phase 2
- chọn ra candidate mạnh nhất để train full và sinh submission mới

## Results

| Run ID | Candidate | Direction | CV Macro F1 | Std |
|---|---|---|---:|---:|
{table_md}

## Winner of Phase 3

- Run ID: `{best_result['run_id']}`
- Candidate: `{best_result['candidate_name']}`
- Direction: `{best_result['direction']}`
- Feature set: `{best_result['feature_set']}`
- Model: `{best_result['model']}`
- CV Macro F1: `{best_result['cv_macro_f1']:.6f}`
- CV std: `{best_result['cv_std']:.6f}`

## Comparison with Phase 2 baseline

- Phase 2 baseline CV: `{baseline_mean:.6f}`
- Phase 3 best CV: `{best_result['cv_macro_f1']:.6f}`
- Absolute improvement: `{improvement:.6f}`

## Submission

- File: `{submission_path.as_posix()}`

## Short interpretation

- Tuning quanh hướng text-first vẫn là hướng hiệu quả nhất cho M1.
- Metadata token augmentation và hybrid sparse chưa thắng được text tuned.
- Insight quan trọng nhất của Phase 3 là `binary word presence` đang mạnh hơn TF-IDF chuẩn trên stage 1 hiện tại.
"""


def main() -> None:
    shared_config = load_config()
    branch_config = load_config(BRANCH_CONFIG_PATH)

    train_df, test_df = load_train_and_test()
    y_train = train_df[shared_config["data"]["target_column"]]
    inputs = build_phase3_inputs(train_df, test_df)

    tracker_path = shared_config["paths"]["experiment_tracker"]
    tracker_df = pd.read_csv(resolve_project_path(tracker_path))
    baseline_row = tracker_df.loc[tracker_df["run_id"] == PHASE2_BASELINE_RUN_ID].iloc[0]
    baseline_mean = float(baseline_row["cv_macro_f1"])

    splitter = build_stratified_kfold(
        n_splits=shared_config["cv"]["n_splits"],
        shuffle=shared_config["cv"]["shuffle"],
        random_state=shared_config["cv"]["random_state"],
    )

    results: list[dict] = []
    candidate_specs = build_phase3_candidate_specs()
    for spec in candidate_specs:
        model = build_candidate_model(spec.name)
        candidate_input = inputs[spec.input_key]
        scores = cross_val_score(model, candidate_input, y_train, cv=splitter, scoring="f1_macro")

        result = {
            "run_id": spec.run_id,
            "candidate_name": spec.name,
            "direction": spec.direction,
            "feature_set": spec.feature_set,
            "model": spec.model_name,
            "cv_macro_f1": float(scores.mean()),
            "cv_std": float(scores.std()),
            "notes": f"phase3 candidate {spec.direction}",
        }
        results.append(result)

        tracker_row = {
            "run_id": spec.run_id,
            "owner": branch_config["branch"]["owner"],
            "branch_name": branch_config["branch"]["name"],
            "feature_set": spec.feature_set,
            "model": spec.model_name,
            "cv_macro_f1": round(float(scores.mean()), 6),
            "cv_std": round(float(scores.std()), 6),
            "public_lb": "",
            "notes": f"phase3 candidate {spec.direction}",
        }
        upsert_csv_row(tracker_row, key_field="run_id", tracker_path=tracker_path)

    results_df = pd.DataFrame(results).sort_values(
        by=["cv_macro_f1", "cv_std"],
        ascending=[False, True],
    )

    best_result = results_df.iloc[0]
    best_spec = next(spec for spec in candidate_specs if spec.run_id == best_result["run_id"])
    best_model = build_candidate_model(best_spec.name)
    best_train_input = inputs[best_spec.input_key]
    best_test_input = inputs[f"test_{best_spec.input_key}"]

    best_model.fit(best_train_input, y_train)
    test_predictions = best_model.predict(best_test_input)

    submission_path = resolve_project_path("data/submissions/sub_m1_v2_phase3_best.csv")
    submission_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            shared_config["data"]["id_column"]: test_df[shared_config["data"]["id_column"]],
            shared_config["data"]["target_column"]: test_predictions,
        }
    ).to_csv(submission_path, index=False)

    results_csv_path = resolve_project_path("reports/battle_m1/phase3_results.csv")
    results_csv_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(results_csv_path, index=False)

    summary_path = resolve_project_path("reports/battle_m1/phase3_experiment_summary.md")
    write_text_file(
        summary_path,
        render_phase3_summary(
            branch_config=branch_config,
            baseline_mean=baseline_mean,
            results_df=results_df,
            best_result=best_result,
            submission_path=submission_path,
        ),
    )

    submission_row = {
        "submission_id": "sub_m1_002",
        "owner": branch_config["branch"]["owner"],
        "branch_name": branch_config["branch"]["name"],
        "file_name": submission_path.name,
        "model_family": "text_tuned_binary",
        "cv_macro_f1": round(float(best_result["cv_macro_f1"]), 6),
        "public_lb": "",
        "notes": f"phase3 best candidate {best_result['candidate_name']}",
    }
    upsert_csv_row(
        submission_row,
        key_field="submission_id",
        tracker_path=shared_config["paths"]["submission_log"],
    )

    print("Phase 3 results:")
    print(results_df[["run_id", "candidate_name", "cv_macro_f1", "cv_std"]].to_string(index=False))
    print(f"\nBest candidate: {best_result['candidate_name']}")
    print(f"Submission saved to: {submission_path}")


if __name__ == "__main__":
    main()
