from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.loading import load_train_and_test
from src.features.text import build_text_series
from src.utils.logging_utils import upsert_csv_row
from src.utils.paths import load_config, resolve_project_path


BRANCH_CONFIG_PATH = "configs/branches/m1_full_pipeline.yaml"
PHASE3_WINNER_RUN_ID = "exp_m1_002"
PHASE3_BACKUP_RUN_ID = "exp_m1_011"


@dataclass(frozen=True)
class SingleCandidate:
    run_id: str
    name: str
    feature_set: str
    model_name: str
    pipeline_key: str
    direction: str


@dataclass(frozen=True)
class EnsembleCandidate:
    run_id: str
    name: str
    feature_set: str
    model_name: str
    members: tuple[tuple[str, float], ...]
    direction: str


def write_text_file(path: Path, content: str) -> None:
    """Write a UTF-8 text file, creating parents when needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_base_text_series(train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Return normalized title series for train and test."""
    return build_text_series(train_df), build_text_series(test_df)


def build_text_model(key: str) -> Pipeline:
    """Build one text-only model candidate."""
    if key == "phase3_best_binary_tfidf_c6":
        vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            binary=True,
            strip_accents="unicode",
        )
        classifier = OneVsRestClassifier(
            LogisticRegression(
                C=6.0,
                max_iter=5000,
                solver="liblinear",
                class_weight="balanced",
                random_state=42,
            )
        )
        return Pipeline([("vectorizer", vectorizer), ("classifier", classifier)])

    if key == "phase3_backup_tfidf_min2_c2":
        vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            min_df=2,
            sublinear_tf=False,
            strip_accents="unicode",
        )
        classifier = OneVsRestClassifier(
            LogisticRegression(
                C=2.0,
                max_iter=5000,
                solver="liblinear",
                class_weight="balanced",
                random_state=42,
            )
        )
        return Pipeline([("vectorizer", vectorizer), ("classifier", classifier)])

    if key == "binary_count_c6":
        vectorizer = CountVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            binary=True,
            strip_accents="unicode",
        )
        classifier = OneVsRestClassifier(
            LogisticRegression(
                C=6.0,
                max_iter=5000,
                solver="liblinear",
                class_weight="balanced",
                random_state=42,
            )
        )
        return Pipeline([("vectorizer", vectorizer), ("classifier", classifier)])

    if key == "binary_tfidf_c4":
        vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            binary=True,
            strip_accents="unicode",
        )
        classifier = OneVsRestClassifier(
            LogisticRegression(
                C=4.0,
                max_iter=5000,
                solver="liblinear",
                class_weight="balanced",
                random_state=42,
            )
        )
        return Pipeline([("vectorizer", vectorizer), ("classifier", classifier)])

    raise ValueError(f"Unknown model key '{key}'.")


def evaluate_single_candidate(
    spec: SingleCandidate,
    X: pd.Series,
    y: np.ndarray,
    splitter: StratifiedKFold,
) -> dict:
    """Evaluate one text-only model with the shared CV splitter."""
    fold_scores: list[float] = []
    for train_idx, valid_idx in splitter.split(X, y):
        model = build_text_model(spec.pipeline_key)
        X_train = X.iloc[train_idx]
        X_valid = X.iloc[valid_idx]
        y_train = y[train_idx]
        y_valid = y[valid_idx]

        model.fit(X_train, y_train)
        predictions = model.predict(X_valid)
        fold_scores.append(f1_score(y_valid, predictions, average="macro"))

    return {
        "run_id": spec.run_id,
        "candidate_name": spec.name,
        "candidate_type": "single_model",
        "direction": spec.direction,
        "feature_set": spec.feature_set,
        "model": spec.model_name,
        "cv_macro_f1": float(np.mean(fold_scores)),
        "cv_std": float(np.std(fold_scores)),
        "fold_scores": [round(score, 6) for score in fold_scores],
    }


def evaluate_ensemble_candidate(
    spec: EnsembleCandidate,
    X: pd.Series,
    y: np.ndarray,
    splitter: StratifiedKFold,
    labels: np.ndarray,
) -> dict:
    """Evaluate one probability-blend ensemble on shared CV."""
    fold_scores: list[float] = []
    for train_idx, valid_idx in splitter.split(X, y):
        X_train = X.iloc[train_idx]
        X_valid = X.iloc[valid_idx]
        y_train = y[train_idx]
        y_valid = y[valid_idx]

        blended_probabilities = None
        for model_key, weight in spec.members:
            model = build_text_model(model_key)
            model.fit(X_train, y_train)
            probabilities = model.predict_proba(X_valid)
            blended_probabilities = (
                probabilities * weight
                if blended_probabilities is None
                else blended_probabilities + probabilities * weight
            )

        predictions = labels[np.argmax(blended_probabilities, axis=1)]
        fold_scores.append(f1_score(y_valid, predictions, average="macro"))

    return {
        "run_id": spec.run_id,
        "candidate_name": spec.name,
        "candidate_type": "ensemble",
        "direction": spec.direction,
        "feature_set": spec.feature_set,
        "model": spec.model_name,
        "cv_macro_f1": float(np.mean(fold_scores)),
        "cv_std": float(np.std(fold_scores)),
        "fold_scores": [round(score, 6) for score in fold_scores],
    }


def fit_predict_ensemble(
    members: tuple[tuple[str, float], ...],
    X_train: pd.Series,
    y_train: np.ndarray,
    X_test: pd.Series,
    labels: np.ndarray,
) -> np.ndarray:
    """Train each ensemble member on full train and blend test probabilities."""
    blended_probabilities = None
    for model_key, weight in members:
        model = build_text_model(model_key)
        model.fit(X_train, y_train)
        probabilities = model.predict_proba(X_test)
        blended_probabilities = (
            probabilities * weight
            if blended_probabilities is None
            else blended_probabilities + probabilities * weight
        )

    return labels[np.argmax(blended_probabilities, axis=1)]


def render_phase4_summary(
    branch_config: dict,
    phase3_mean: float,
    results_df: pd.DataFrame,
    best_result: pd.Series,
    submission_path: Path,
) -> str:
    """Render the phase-4 summary markdown."""
    rows = []
    for _, row in results_df.iterrows():
        rows.append(
            f"| {row['run_id']} | {row['candidate_name']} | {row['candidate_type']} | {row['direction']} | {row['cv_macro_f1']:.6f} | {row['cv_std']:.6f} |"
        )
    rows_md = "\n".join(rows)
    improvement = best_result["cv_macro_f1"] - phase3_mean

    return f"""# Phase 4 Text-Only Optimization Summary - M1

## Branch info

- Owner: {branch_config["branch"]["owner"]}
- Branch: `{branch_config["branch"]["name"]}`
- Phase 4 focus: continue optimizing around the strongest text-only family

## Goal of this phase

- giữ trọng tâm vào text-only
- kiểm tra xem representation hoặc blend giữa các model text mạnh có giúp tăng điểm không
- chốt candidate tốt nhất cho sprint tiếp theo

## Results

| Run ID | Candidate | Type | Direction | CV Macro F1 | Std |
|---|---|---|---|---:|---:|
{rows_md}

## Winner of Phase 4

- Run ID: `{best_result['run_id']}`
- Candidate: `{best_result['candidate_name']}`
- Type: `{best_result['candidate_type']}`
- Direction: `{best_result['direction']}`
- CV Macro F1: `{best_result['cv_macro_f1']:.6f}`
- CV std: `{best_result['cv_std']:.6f}`

## Comparison with previous best

- Phase 3 best CV: `{phase3_mean:.6f}`
- Phase 4 best CV: `{best_result['cv_macro_f1']:.6f}`
- Absolute improvement: `{improvement:.6f}`

## Submission

- File: `{submission_path.as_posix()}`

## Short interpretation

- Text-only vẫn là hướng đúng của M1.
- Representation tốt nhất đơn lẻ vẫn là `binary word presence + OVR Logistic Regression`.
- Tuy nhiên blend giữa candidate mạnh nhất và candidate backup ổn định đã cho mean tốt hơn và std thấp hơn, nên Phase 4 winner là một text-only ensemble chứ không phải single model.
"""


def main() -> None:
    shared_config = load_config()
    branch_config = load_config(BRANCH_CONFIG_PATH)

    train_df, test_df = load_train_and_test()
    train_text, test_text = build_base_text_series(train_df, test_df)
    y_train = train_df[shared_config["data"]["target_column"]].to_numpy()
    labels = np.sort(np.unique(y_train))

    splitter = StratifiedKFold(
        n_splits=shared_config["cv"]["n_splits"],
        shuffle=shared_config["cv"]["shuffle"],
        random_state=shared_config["cv"]["random_state"],
    )

    tracker_df = pd.read_csv(resolve_project_path(shared_config["paths"]["experiment_tracker"]))
    phase3_mean = float(
        tracker_df.loc[tracker_df["run_id"] == PHASE3_WINNER_RUN_ID, "cv_macro_f1"].iloc[0]
    )
    phase3_backup_mean = float(
        tracker_df.loc[tracker_df["run_id"] == PHASE3_BACKUP_RUN_ID, "cv_macro_f1"].iloc[0]
    )
    phase3_backup_std = float(
        tracker_df.loc[tracker_df["run_id"] == PHASE3_BACKUP_RUN_ID, "cv_std"].iloc[0]
    )

    single_specs = [
        SingleCandidate(
            run_id="exp_m1_012",
            name="binary_count_c6",
            feature_set="title_clean_word12_binary_count",
            model_name="ovr_logistic_regression",
            pipeline_key="binary_count_c6",
            direction="text_representation_variant",
        ),
        SingleCandidate(
            run_id="exp_m1_013",
            name="binary_tfidf_c4",
            feature_set="title_clean_word12_binary",
            model_name="ovr_logistic_regression",
            pipeline_key="binary_tfidf_c4",
            direction="text_representation_variant",
        ),
    ]
    ensemble_specs = [
        EnsembleCandidate(
            run_id="exp_m1_014",
            name="ens_best_backup_50_50",
            feature_set="blend_binary_tfidf_c6__tfidf_min2_c2",
            model_name="probability_blend",
            members=(
                ("phase3_best_binary_tfidf_c6", 0.5),
                ("phase3_backup_tfidf_min2_c2", 0.5),
            ),
            direction="text_only_ensemble",
        ),
        EnsembleCandidate(
            run_id="exp_m1_015",
            name="ens_best_backup_40_60",
            feature_set="blend_binary_tfidf_c6__tfidf_min2_c2",
            model_name="probability_blend",
            members=(
                ("phase3_best_binary_tfidf_c6", 0.4),
                ("phase3_backup_tfidf_min2_c2", 0.6),
            ),
            direction="text_only_ensemble",
        ),
        EnsembleCandidate(
            run_id="exp_m1_016",
            name="ens_best_backup_55_45",
            feature_set="blend_binary_tfidf_c6__tfidf_min2_c2",
            model_name="probability_blend",
            members=(
                ("phase3_best_binary_tfidf_c6", 0.55),
                ("phase3_backup_tfidf_min2_c2", 0.45),
            ),
            direction="text_only_ensemble",
        ),
    ]

    results: list[dict] = []
    for spec in single_specs:
        result = evaluate_single_candidate(spec, train_text, y_train, splitter)
        results.append(result)

        tracker_row = {
            "run_id": spec.run_id,
            "owner": branch_config["branch"]["owner"],
            "branch_name": branch_config["branch"]["name"],
            "feature_set": spec.feature_set,
            "model": spec.model_name,
            "cv_macro_f1": round(result["cv_macro_f1"], 6),
            "cv_std": round(result["cv_std"], 6),
            "public_lb": "",
            "notes": f"phase4 candidate {spec.direction}",
        }
        upsert_csv_row(
            tracker_row,
            key_field="run_id",
            tracker_path=shared_config["paths"]["experiment_tracker"],
        )

    for spec in ensemble_specs:
        result = evaluate_ensemble_candidate(spec, train_text, y_train, splitter, labels)
        results.append(result)

        tracker_row = {
            "run_id": spec.run_id,
            "owner": branch_config["branch"]["owner"],
            "branch_name": branch_config["branch"]["name"],
            "feature_set": spec.feature_set,
            "model": spec.model_name,
            "cv_macro_f1": round(result["cv_macro_f1"], 6),
            "cv_std": round(result["cv_std"], 6),
            "public_lb": "",
            "notes": f"phase4 candidate {spec.direction}",
        }
        upsert_csv_row(
            tracker_row,
            key_field="run_id",
            tracker_path=shared_config["paths"]["experiment_tracker"],
        )

    results_df = pd.DataFrame(results).sort_values(
        by=["cv_macro_f1", "cv_std"],
        ascending=[False, True],
    )

    best_result = results_df.iloc[0]
    best_ensemble_spec = next(spec for spec in ensemble_specs if spec.run_id == best_result["run_id"])
    test_predictions = fit_predict_ensemble(
        members=best_ensemble_spec.members,
        X_train=train_text,
        y_train=y_train,
        X_test=test_text,
        labels=labels,
    )

    submission_path = resolve_project_path("data/submissions/sub_m1_v3_phase4_text_ensemble.csv")
    submission_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            shared_config["data"]["id_column"]: test_df[shared_config["data"]["id_column"]],
            shared_config["data"]["target_column"]: test_predictions,
        }
    ).to_csv(submission_path, index=False)

    results_csv_path = resolve_project_path("reports/battle_m1/phase4_results.csv")
    results_csv_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(results_csv_path, index=False)

    summary_path = resolve_project_path("reports/battle_m1/phase4_experiment_summary.md")
    write_text_file(
        summary_path,
        render_phase4_summary(
            branch_config=branch_config,
            phase3_mean=phase3_mean,
            results_df=results_df,
            best_result=best_result,
            submission_path=submission_path,
        ),
    )

    submission_row = {
        "submission_id": "sub_m1_003",
        "owner": branch_config["branch"]["owner"],
        "branch_name": branch_config["branch"]["name"],
        "file_name": submission_path.name,
        "model_family": "text_only_ensemble",
        "cv_macro_f1": round(float(best_result["cv_macro_f1"]), 6),
        "public_lb": "",
        "notes": f"phase4 best candidate {best_result['candidate_name']}",
    }
    upsert_csv_row(
        submission_row,
        key_field="submission_id",
        tracker_path=shared_config["paths"]["submission_log"],
    )

    print("Phase 4 results:")
    print(results_df[["run_id", "candidate_name", "cv_macro_f1", "cv_std"]].to_string(index=False))
    print(f"\nPhase 3 winner mean: {phase3_mean:.6f}")
    print(f"Phase 3 backup mean/std: {phase3_backup_mean:.6f} / {phase3_backup_std:.6f}")
    print(f"Phase 4 best candidate: {best_result['candidate_name']}")
    print(f"Submission saved to: {submission_path}")


if __name__ == "__main__":
    main()
