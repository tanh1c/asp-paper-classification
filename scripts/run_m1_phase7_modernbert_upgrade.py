from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.loading import load_train_and_test
from src.features.text import build_structured_text_series, build_text_series
from src.utils.logging_utils import upsert_csv_row
from src.utils.paths import load_config, resolve_project_path


BRANCH_CONFIG_PATH = "configs/branches/m1_full_pipeline.yaml"
PHASE4_REFERENCE_RUN_ID = "exp_m1_014"
ENCODER_MODEL_ID = "nomic-ai/modernbert-embed-base"
EMBEDDING_BATCH_SIZE = 16
STRUCTURED_C_SWEEP = (1.0, 2.0, 4.0, 8.0, 16.0)
TITLE_ONLY_C_SWEEP = (1.0, 2.0, 4.0, 8.0, 16.0)
BLEND_C_SWEEP = (1.5, 2.0, 2.5, 3.0, 3.5)
BLEND_WEIGHT_SWEEP = (0.50, 0.52, 0.54, 0.55, 0.56, 0.58, 0.60)


@dataclass(frozen=True)
class OfficialCandidate:
    run_id: str
    candidate_key: str
    notes: str


def write_text_file(path: Path, content: str) -> None:
    """Write UTF-8 content while creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_phase3_best_model() -> Pipeline:
    """Return the phase-3 best sparse text model."""
    return Pipeline(
        [
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
    """Return the lower-variance sparse backup used in the phase-4 ensemble."""
    return Pipeline(
        [
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


def align_probabilities(
    probabilities: np.ndarray,
    seen_labels: np.ndarray,
    all_labels: np.ndarray,
) -> np.ndarray:
    """Align probability columns to the shared sorted label order."""
    aligned = np.zeros((probabilities.shape[0], len(all_labels)), dtype=float)
    for column_index, label in enumerate(seen_labels):
        target_index = int(np.where(all_labels == label)[0][0])
        aligned[:, target_index] = probabilities[:, column_index]
    return aligned


def encode_variant_texts(
    encoder: SentenceTransformer,
    variant_texts: dict[str, pd.Series],
) -> dict[str, np.ndarray]:
    """Encode each text variant once to reuse across all CV sweeps."""
    encoded: dict[str, np.ndarray] = {}
    for variant_name, texts in variant_texts.items():
        encoded[variant_name] = encoder.encode(
            texts.tolist(),
            normalize_embeddings=True,
            batch_size=EMBEDDING_BATCH_SIZE,
            show_progress_bar=False,
        )
    return encoded


def build_phase4_reference_fold_probabilities(
    title_text: pd.Series,
    y_train: np.ndarray,
    splitter: StratifiedKFold,
    labels: np.ndarray,
) -> tuple[list[tuple[np.ndarray, np.ndarray]], list[np.ndarray], dict]:
    """Precompute phase-4 ensemble probabilities on each CV fold."""
    fold_indices: list[tuple[np.ndarray, np.ndarray]] = []
    fold_probabilities: list[np.ndarray] = []
    fold_scores: list[float] = []

    for train_idx, valid_idx in splitter.split(title_text, y_train):
        best_model = build_phase3_best_model()
        backup_model = build_phase3_backup_model()

        best_model.fit(title_text.iloc[train_idx], y_train[train_idx])
        backup_model.fit(title_text.iloc[train_idx], y_train[train_idx])

        best_prob = align_probabilities(
            best_model.predict_proba(title_text.iloc[valid_idx]),
            best_model.classes_,
            labels,
        )
        backup_prob = align_probabilities(
            backup_model.predict_proba(title_text.iloc[valid_idx]),
            backup_model.classes_,
            labels,
        )
        ensemble_prob = 0.5 * best_prob + 0.5 * backup_prob
        ensemble_pred = labels[np.argmax(ensemble_prob, axis=1)]

        fold_indices.append((train_idx, valid_idx))
        fold_probabilities.append(ensemble_prob)
        fold_scores.append(f1_score(y_train[valid_idx], ensemble_pred, average="macro"))

    diagnostics = {
        "cv_macro_f1": float(np.mean(fold_scores)),
        "cv_std": float(np.std(fold_scores)),
        "fold_scores": [round(score, 6) for score in fold_scores],
    }
    return fold_indices, fold_probabilities, diagnostics


def evaluate_standalone_encoder(
    variant_name: str,
    embeddings: np.ndarray,
    c_value: float,
    y_train: np.ndarray,
    splitter: StratifiedKFold,
) -> dict:
    """Evaluate one frozen-encoder + logistic-regression candidate."""
    fold_scores: list[float] = []

    for train_idx, valid_idx in splitter.split(embeddings, y_train):
        classifier = LogisticRegression(
            C=c_value,
            max_iter=4000,
            class_weight="balanced",
            random_state=42,
        )
        classifier.fit(embeddings[train_idx], y_train[train_idx])
        predictions = classifier.predict(embeddings[valid_idx])
        fold_scores.append(f1_score(y_train[valid_idx], predictions, average="macro"))

    candidate_key = f"modernbert_{variant_name}_c{str(c_value).replace('.', '_')}"
    return {
        "candidate_key": candidate_key,
        "candidate_group": "standalone_encoder",
        "variant_name": variant_name,
        "encoder_model": ENCODER_MODEL_ID,
        "phase4_weight": 0.0,
        "modernbert_weight": 1.0,
        "logreg_c": float(c_value),
        "cv_macro_f1": float(np.mean(fold_scores)),
        "cv_std": float(np.std(fold_scores)),
        "fold_scores": [round(score, 6) for score in fold_scores],
    }


def evaluate_blended_encoder_candidate(
    embeddings: np.ndarray,
    c_value: float,
    modernbert_weight: float,
    y_train: np.ndarray,
    labels: np.ndarray,
    fold_indices: list[tuple[np.ndarray, np.ndarray]],
    phase4_fold_probabilities: list[np.ndarray],
) -> dict:
    """Evaluate one ModernBERT-plus-sparse probability blend."""
    fold_scores: list[float] = []

    for (train_idx, valid_idx), phase4_probabilities in zip(fold_indices, phase4_fold_probabilities):
        classifier = LogisticRegression(
            C=c_value,
            max_iter=4000,
            class_weight="balanced",
            random_state=42,
        )
        classifier.fit(embeddings[train_idx], y_train[train_idx])
        encoder_probabilities = align_probabilities(
            classifier.predict_proba(embeddings[valid_idx]),
            classifier.classes_,
            labels,
        )
        blended_probabilities = (
            (1.0 - modernbert_weight) * phase4_probabilities
            + modernbert_weight * encoder_probabilities
        )
        predictions = labels[np.argmax(blended_probabilities, axis=1)]
        fold_scores.append(f1_score(y_train[valid_idx], predictions, average="macro"))

    candidate_key = (
        "phase4_modernbert_structured_"
        f"c{str(c_value).replace('.', '_')}_"
        f"w{str(modernbert_weight).replace('.', '_')}"
    )
    return {
        "candidate_key": candidate_key,
        "candidate_group": "lexical_semantic_blend",
        "variant_name": "structured",
        "encoder_model": ENCODER_MODEL_ID,
        "phase4_weight": float(1.0 - modernbert_weight),
        "modernbert_weight": float(modernbert_weight),
        "logreg_c": float(c_value),
        "cv_macro_f1": float(np.mean(fold_scores)),
        "cv_std": float(np.std(fold_scores)),
        "fold_scores": [round(score, 6) for score in fold_scores],
    }


def fit_phase4_test_probabilities(
    train_text: pd.Series,
    test_text: pd.Series,
    y_train: np.ndarray,
    labels: np.ndarray,
) -> np.ndarray:
    """Train the phase-4 sparse ensemble on full train and return test probabilities."""
    best_model = build_phase3_best_model()
    backup_model = build_phase3_backup_model()

    best_model.fit(train_text, y_train)
    backup_model.fit(train_text, y_train)

    best_prob = align_probabilities(best_model.predict_proba(test_text), best_model.classes_, labels)
    backup_prob = align_probabilities(
        backup_model.predict_proba(test_text),
        backup_model.classes_,
        labels,
    )
    return 0.5 * best_prob + 0.5 * backup_prob


def build_shortlist_rows(results_df: pd.DataFrame) -> list[OfficialCandidate]:
    """Choose the official candidates that should be logged into the shared tracker."""
    title_only_best = results_df.loc[
        results_df["candidate_group"].eq("standalone_encoder")
        & results_df["variant_name"].eq("title_only")
    ].sort_values(by=["cv_macro_f1", "cv_std"], ascending=[False, True]).iloc[0]

    standalone_best = results_df.loc[
        results_df["candidate_group"].eq("standalone_encoder")
        & results_df["variant_name"].eq("structured")
    ].sort_values(by=["cv_macro_f1", "cv_std"], ascending=[False, True]).iloc[0]

    blend_rows = results_df.loc[results_df["candidate_group"].eq("lexical_semantic_blend")].sort_values(
        by=["cv_macro_f1", "cv_std"],
        ascending=[False, True],
    )
    blend_best = blend_rows.iloc[0]
    blend_runner_up = blend_rows.iloc[1]

    return [
        OfficialCandidate(
            run_id="exp_m1_017",
            candidate_key=str(title_only_best["candidate_key"]),
            notes="phase7 best title-only ModernBERT encoder",
        ),
        OfficialCandidate(
            run_id="exp_m1_018",
            candidate_key=str(standalone_best["candidate_key"]),
            notes="phase7 best standalone structured ModernBERT encoder",
        ),
        OfficialCandidate(
            run_id="exp_m1_019",
            candidate_key=str(blend_best["candidate_key"]),
            notes="phase7 best lexical-semantic blend",
        ),
        OfficialCandidate(
            run_id="exp_m1_020",
            candidate_key=str(blend_runner_up["candidate_key"]),
            notes="phase7 runner-up lexical-semantic blend",
        ),
    ]


def render_phase7_summary(
    branch_config: dict,
    phase4_reference: pd.Series,
    results_df: pd.DataFrame,
    best_result: pd.Series,
    submission_path: Path,
) -> str:
    """Render the markdown summary for the ModernBERT upgrade phase."""
    top_rows = results_df.head(10)
    table_rows = []
    for _, row in top_rows.iterrows():
        table_rows.append(
            f"| {row['candidate_key']} | {row['candidate_group']} | {row['variant_name']} | {row['logreg_c']:.2f} | {row['modernbert_weight']:.2f} | {row['cv_macro_f1']:.6f} | {row['cv_std']:.6f} |"
        )

    improvement = float(best_result["cv_macro_f1"]) - float(phase4_reference["cv_macro_f1"])
    return f"""# Phase 7 ModernBERT Upgrade Summary - M1

## Branch info

- Owner: {branch_config["branch"]["owner"]}
- Branch: `{branch_config["branch"]["name"]}`
- Goal of this phase: push M1 beyond sparse text baselines with a modern transformer encoder
- Encoder family used: `ModernBERT`
- Encoder checkpoint: `{ENCODER_MODEL_ID}`

## Why this phase was designed this way

- User feedback from Kaggle was clear: M1 needed a less thô sơ text method than TF-IDF-only baselines.
- The current machine is CPU-only, so a frozen encoder plus linear head was the fastest reliable way to test transformer signal at competition speed.
- Instead of replacing the sparse winner blindly, this phase tests whether a semantic encoder can **complement** the lexical n-gram ensemble that already works well.

## Phase-4 reference

- Run ID: `{phase4_reference['run_id']}`
- Candidate: `phase4_text_only_ensemble`
- CV Macro F1: `{phase4_reference['cv_macro_f1']:.6f}`
- CV std: `{phase4_reference['cv_std']:.6f}`

## Top phase-7 candidates

| Candidate | Group | Text Variant | C | ModernBERT Weight | CV Macro F1 | Std |
|---|---|---|---:|---:|---:|---:|
{chr(10).join(table_rows)}

## Winner of Phase 7

- Candidate key: `{best_result['candidate_key']}`
- Group: `{best_result['candidate_group']}`
- Text variant: `{best_result['variant_name']}`
- ModernBERT logistic `C`: `{best_result['logreg_c']:.2f}`
- Blend weights:
  - sparse phase-4 ensemble: `{best_result['phase4_weight']:.2f}`
  - ModernBERT encoder model: `{best_result['modernbert_weight']:.2f}`
- CV Macro F1: `{best_result['cv_macro_f1']:.6f}`
- CV std: `{best_result['cv_std']:.6f}`

## Comparison with previous M1 winner

- Phase-4 best CV: `{phase4_reference['cv_macro_f1']:.6f}`
- Phase-7 best CV: `{best_result['cv_macro_f1']:.6f}`
- Absolute improvement: `{improvement:.6f}`

## Interpretation

- Pure ModernBERT encoder features already become competitive on this dataset, especially when the input text includes `title + venue + year + authors`.
- The strongest result does **not** come from throwing away sparse features. It comes from blending:
  - lexical precision from the phase-4 TF-IDF ensemble
  - semantic compression from ModernBERT embeddings
- This is exactly the kind of complementarity we want for a small competition dataset: one model catches exact n-grams, the other smooths over wording variation and topic similarity.

## Submission

- New file: `{submission_path.as_posix()}`

## Recommendation

- Replace the old M1 main candidate with this phase-7 ModernBERT blend.
- Keep the old phase-4 ensemble as a lexical fallback.
- Keep the best standalone structured ModernBERT encoder as a semantic backup if Kaggle later disagrees with the blend.
"""


def main() -> None:
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

    shared_config = load_config()
    branch_config = load_config(BRANCH_CONFIG_PATH)

    train_df, test_df = load_train_and_test()
    title_train = build_text_series(train_df)
    title_test = build_text_series(test_df)
    encoder_title_train = build_text_series(train_df, normalize=False)
    encoder_structured_train = build_structured_text_series(train_df, normalize_columns=False)
    encoder_structured_test = build_structured_text_series(test_df, normalize_columns=False)
    y_train = train_df[shared_config["data"]["target_column"]].to_numpy()
    labels = np.sort(np.unique(y_train))

    splitter = StratifiedKFold(
        n_splits=shared_config["cv"]["n_splits"],
        shuffle=shared_config["cv"]["shuffle"],
        random_state=shared_config["cv"]["random_state"],
    )

    tracker_df = pd.read_csv(resolve_project_path(shared_config["paths"]["experiment_tracker"]))
    phase4_reference = tracker_df.loc[tracker_df["run_id"] == PHASE4_REFERENCE_RUN_ID].iloc[0]

    encoder = SentenceTransformer(ENCODER_MODEL_ID)
    variant_texts = {
        "title_only": encoder_title_train,
        "structured": encoder_structured_train,
    }
    encoded_variants = encode_variant_texts(encoder, variant_texts)

    fold_indices, phase4_fold_probabilities, phase4_diagnostics = build_phase4_reference_fold_probabilities(
        title_text=title_train,
        y_train=y_train,
        splitter=splitter,
        labels=labels,
    )

    results: list[dict] = [
        {
            "candidate_key": "phase4_reference_text_only_ensemble",
            "candidate_group": "phase4_reference",
            "variant_name": "title_only",
            "encoder_model": "",
            "phase4_weight": 1.0,
            "modernbert_weight": 0.0,
            "logreg_c": 0.0,
            "cv_macro_f1": phase4_diagnostics["cv_macro_f1"],
            "cv_std": phase4_diagnostics["cv_std"],
            "fold_scores": phase4_diagnostics["fold_scores"],
        }
    ]

    for c_value in TITLE_ONLY_C_SWEEP:
        results.append(
            evaluate_standalone_encoder(
                variant_name="title_only",
                embeddings=encoded_variants["title_only"],
                c_value=c_value,
                y_train=y_train,
                splitter=splitter,
            )
        )

    for c_value in STRUCTURED_C_SWEEP:
        results.append(
            evaluate_standalone_encoder(
                variant_name="structured",
                embeddings=encoded_variants["structured"],
                c_value=c_value,
                y_train=y_train,
                splitter=splitter,
            )
        )

    for c_value in BLEND_C_SWEEP:
        for modernbert_weight in BLEND_WEIGHT_SWEEP:
            results.append(
                evaluate_blended_encoder_candidate(
                    embeddings=encoded_variants["structured"],
                    c_value=c_value,
                    modernbert_weight=modernbert_weight,
                    y_train=y_train,
                    labels=labels,
                    fold_indices=fold_indices,
                    phase4_fold_probabilities=phase4_fold_probabilities,
                )
            )

    results_df = pd.DataFrame(results).sort_values(
        by=["cv_macro_f1", "cv_std", "candidate_key"],
        ascending=[False, True, True],
    )
    best_result = results_df.iloc[0]

    shortlist = build_shortlist_rows(results_df)
    shortlist_lookup = {item.candidate_key: item for item in shortlist}
    results_df["official_run_id"] = results_df["candidate_key"].map(
        lambda key: shortlist_lookup[key].run_id if key in shortlist_lookup else ""
    )

    results_csv_path = resolve_project_path("reports/battle_m1/phase7_transformer_results.csv")
    results_csv_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(results_csv_path, index=False)

    modern_c = float(best_result["logreg_c"])
    modern_weight = float(best_result["modernbert_weight"])
    phase4_weight = float(best_result["phase4_weight"])

    modern_classifier = LogisticRegression(
        C=modern_c,
        max_iter=4000,
        class_weight="balanced",
        random_state=42,
    )
    modern_classifier.fit(encoded_variants["structured"], y_train)
    test_embeddings = encoder.encode(
        encoder_structured_test.tolist(),
        normalize_embeddings=True,
        batch_size=EMBEDDING_BATCH_SIZE,
        show_progress_bar=False,
    )
    modern_test_probabilities = align_probabilities(
        modern_classifier.predict_proba(test_embeddings),
        modern_classifier.classes_,
        labels,
    )
    phase4_test_probabilities = fit_phase4_test_probabilities(
        train_text=title_train,
        test_text=title_test,
        y_train=y_train,
        labels=labels,
    )

    if best_result["candidate_group"] == "lexical_semantic_blend":
        final_probabilities = phase4_weight * phase4_test_probabilities + modern_weight * modern_test_probabilities
    elif best_result["candidate_group"] == "standalone_encoder":
        final_probabilities = modern_test_probabilities
    else:
        final_probabilities = phase4_test_probabilities

    test_predictions = labels[np.argmax(final_probabilities, axis=1)]
    submission_path = resolve_project_path("data/submissions/sub_m1_v4_phase7_modernbert_blend.csv")
    submission_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            shared_config["data"]["id_column"]: test_df[shared_config["data"]["id_column"]],
            shared_config["data"]["target_column"]: test_predictions,
        }
    ).to_csv(submission_path, index=False)

    summary_path = resolve_project_path("reports/battle_m1/phase7_transformer_summary.md")
    write_text_file(
        summary_path,
        render_phase7_summary(
            branch_config=branch_config,
            phase4_reference=phase4_reference,
            results_df=results_df,
            best_result=best_result,
            submission_path=submission_path,
        ),
    )

    for official_candidate in shortlist:
        row = results_df.loc[results_df["candidate_key"] == official_candidate.candidate_key].iloc[0]
        tracker_row = {
            "run_id": official_candidate.run_id,
            "owner": branch_config["branch"]["owner"],
            "branch_name": branch_config["branch"]["name"],
            "feature_set": (
                "structured_modernbert_embeddings"
                if row["variant_name"] == "structured"
                else "title_only_modernbert_embeddings"
            ),
            "model": (
                "modernbert_logreg_blend"
                if row["candidate_group"] == "lexical_semantic_blend"
                else "modernbert_logistic_regression"
            ),
            "cv_macro_f1": round(float(row["cv_macro_f1"]), 6),
            "cv_std": round(float(row["cv_std"]), 6),
            "public_lb": "",
            "notes": official_candidate.notes,
        }
        upsert_csv_row(
            tracker_row,
            key_field="run_id",
            tracker_path=shared_config["paths"]["experiment_tracker"],
        )

    submission_row = {
        "submission_id": "sub_m1_004",
        "owner": branch_config["branch"]["owner"],
        "branch_name": branch_config["branch"]["name"],
        "file_name": submission_path.name,
        "model_family": "modernbert_sparse_blend",
        "cv_macro_f1": round(float(best_result["cv_macro_f1"]), 6),
        "public_lb": "",
        "notes": f"phase7 best candidate {best_result['candidate_key']}",
    }
    upsert_csv_row(
        submission_row,
        key_field="submission_id",
        tracker_path=shared_config["paths"]["submission_log"],
    )

    print("Top phase-7 candidates:")
    print(
        results_df[
            [
                "candidate_key",
                "candidate_group",
                "variant_name",
                "logreg_c",
                "modernbert_weight",
                "cv_macro_f1",
                "cv_std",
            ]
        ].head(10).to_string(index=False)
    )
    print(f"\nPhase-4 reference CV: {float(phase4_reference['cv_macro_f1']):.6f}")
    print(f"Phase-7 best CV: {float(best_result['cv_macro_f1']):.6f}")
    print(f"Submission saved to: {submission_path}")


if __name__ == "__main__":
    main()
