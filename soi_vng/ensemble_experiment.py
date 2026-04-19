from __future__ import annotations

import argparse
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.kernel_approximation import AdditiveChi2Sampler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import FeatureUnion
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import LinearSVC


ROOT_DIR = Path(__file__).resolve().parent.parent
SOI_DIR = Path(__file__).resolve().parent
TRAIN_PATH = ROOT_DIR / "dataset_stage1" / "Stage_1_publcitrain.csv"
TEST_PATH = ROOT_DIR / "dataset_stage1" / "test (2).csv"
OUTPUT_DIR = SOI_DIR / "ensemble_outputs"
FEATURE_PREVIEW_DIR = OUTPUT_DIR / "feature_previews"

LABEL_COL = "Label"
ID_COL = "id"
RANDOM_STATE = 42
warnings.filterwarnings("ignore", category=FutureWarning)


def clean_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value).lower()
    text = re.sub(r"[^a-z0-9+\-#/.: ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_authors(value: object) -> list[str]:
    if pd.isna(value):
        return []
    authors = []
    for item in str(value).split(","):
        author = clean_text(item)
        if author:
            authors.append(author)
    return authors


def doi_prefix(value: object) -> str:
    if pd.isna(value):
        return "__missing__"
    text = str(value).strip().lower()
    if not text:
        return "__missing__"
    return text.split("/", 1)[0]


def doi_suffix_head(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    if "/" not in text:
        return ""

    suffix = text.split("/", 1)[1]
    match = re.search(r"[a-z]+", suffix)
    if not match:
        return ""
    return match.group(0)


class MetadataBuilder:
    def __init__(self, rare_threshold: int = 2) -> None:
        self.rare_threshold = rare_threshold
        self.venue_keep_: set[str] = set()
        self.doi_prefix_keep_: set[str] = set()
        self.doi_suffix_head_keep_: set[str] = set()
        self.columns_: list[str] = []
        self.year_mean_: float = 0.0
        self.year_std_: float = 1.0
        self.year_max_: float = 0.0

    def fit(self, df: pd.DataFrame) -> "MetadataBuilder":
        venues = df["venue"].fillna("__missing__").map(clean_text)
        prefixes = df["doi"].map(doi_prefix)
        suffix_heads = df["doi"].map(doi_suffix_head).replace("", "__missing__")

        self.venue_keep_ = {
            key for key, value in venues.value_counts().items() if value >= self.rare_threshold
        }
        self.doi_prefix_keep_ = {
            key for key, value in prefixes.value_counts().items() if value >= self.rare_threshold
        }
        self.doi_suffix_head_keep_ = {
            key
            for key, value in suffix_heads.value_counts().items()
            if value >= self.rare_threshold
        }

        year = pd.to_numeric(df["year"], errors="coerce")
        self.year_mean_ = float(year.mean()) if year.notna().any() else 0.0
        std = float(year.std()) if year.notna().sum() > 1 else 1.0
        self.year_std_ = std if std > 0 else 1.0
        self.year_max_ = float(year.max()) if year.notna().any() else self.year_mean_

        built = self._build(df)
        self.columns_ = built.columns.tolist()
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        built = self._build(df)
        return built.reindex(columns=self.columns_, fill_value=0)

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.fit(df).transform(df)

    def _build(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame(index=df.index)

        title = df["title"].fillna("").astype(str)
        title_words = title.map(lambda value: value.split())
        out["title_char_count"] = title.str.len()
        out["title_word_count"] = title_words.map(len)
        out["title_avg_word_length"] = title_words.map(
            lambda words: float(np.mean([len(word) for word in words])) if words else 0.0
        )
        out["title_has_colon"] = title.str.contains(":", regex=False).astype(int)
        out["title_has_question"] = title.str.contains("?", regex=False).astype(int)

        year = pd.to_numeric(df["year"], errors="coerce")
        year_filled = year.fillna(self.year_mean_)
        out["year_is_missing"] = year.isna().astype(int)
        out["year_normalized"] = (year_filled - self.year_mean_) / self.year_std_
        out["paper_age"] = self.year_max_ - year_filled

        doi = df["doi"].fillna("").astype(str)
        out["has_doi"] = doi.str.strip().ne("").astype(int)
        out["doi_length"] = doi.str.len()
        out["doi_digit_count"] = doi.str.count(r"\d")
        out["doi_slash_count"] = doi.str.count("/")
        out["doi_dot_count"] = doi.str.count(r"\.")
        out["doi_suffix_head_missing"] = df["doi"].map(doi_suffix_head).eq("").astype(int)

        venue = df["venue"].fillna("__missing__").map(clean_text)
        venue = venue.map(lambda value: value if value in self.venue_keep_ else "__rare__")
        prefix = df["doi"].map(doi_prefix)
        prefix = prefix.map(lambda value: value if value in self.doi_prefix_keep_ else "__rare__")
        suffix_head = df["doi"].map(doi_suffix_head).replace("", "__missing__")
        suffix_head = suffix_head.map(
            lambda value: value if value in self.doi_suffix_head_keep_ else "__rare__"
        )

        categories = pd.get_dummies(
            pd.DataFrame(
                {
                    "venue": venue,
                    "doi_prefix": prefix,
                    "doi_suffix_head": suffix_head,
                }
            ),
            columns=["venue", "doi_prefix", "doi_suffix_head"],
            dtype=int,
        )
        out = pd.concat([out, categories], axis=1)
        return out


def make_text_vectorizer() -> FeatureUnion:
    return FeatureUnion(
        [
            (
                "word",
                TfidfVectorizer(
                    preprocessor=clean_text,
                    analyzer="word",
                    ngram_range=(1, 2),
                    min_df=1,
                    sublinear_tf=True,
                    stop_words="english",
                ),
            ),
            (
                "char",
                TfidfVectorizer(
                    preprocessor=clean_text,
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=1,
                    sublinear_tf=True,
                ),
            ),
        ]
    )


def make_logistic() -> LogisticRegression:
    return LogisticRegression(
        penalty="elasticnet",
        solver="saga",
        l1_ratio=0.35,
        C=3.0,
        max_iter=4000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )


def make_svm() -> CalibratedClassifierCV:
    svm = LinearSVC(C=1.0, class_weight="balanced", random_state=RANDOM_STATE)
    return CalibratedClassifierCV(svm, cv=3)


def make_chi2_svm() -> CalibratedClassifierCV:
    svm = LinearSVC(C=1.0, class_weight="balanced", random_state=RANDOM_STATE)
    return CalibratedClassifierCV(svm, cv=3)


def make_boosting_model():
    try:
        from lightgbm import LGBMClassifier

        return LGBMClassifier(
            n_estimators=300,
            learning_rate=0.04,
            num_leaves=31,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            verbose=-1,
        ), "lightgbm"
    except Exception:
        return (
            HistGradientBoostingClassifier(
                learning_rate=0.04,
                max_iter=250,
                l2_regularization=0.05,
                random_state=RANDOM_STATE,
            ),
            "hist_gradient_boosting",
        )


def predict_aligned_proba(model, x, model_classes: np.ndarray, all_classes: np.ndarray) -> np.ndarray:
    raw = model.predict_proba(x)
    aligned = np.zeros((raw.shape[0], len(all_classes)), dtype=float)
    class_to_pos = {label: pos for pos, label in enumerate(all_classes)}
    for raw_pos, label in enumerate(model_classes):
        aligned[:, class_to_pos[label]] = raw[:, raw_pos]
    return aligned


def build_dense_boost_features(
    train_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    train_text_matrix,
    valid_text_matrix,
    n_components: int,
):
    metadata = MetadataBuilder(rare_threshold=2)
    x_meta_train = metadata.fit_transform(train_df)
    x_meta_valid = metadata.transform(valid_df)

    scaler = StandardScaler()
    x_meta_train_scaled = scaler.fit_transform(x_meta_train)
    x_meta_valid_scaled = scaler.transform(x_meta_valid)

    max_components = min(n_components, train_text_matrix.shape[0] - 1, train_text_matrix.shape[1] - 1)
    if max_components >= 2:
        svd = TruncatedSVD(n_components=max_components, random_state=RANDOM_STATE)
        x_svd_train = svd.fit_transform(train_text_matrix)
        x_svd_valid = svd.transform(valid_text_matrix)
    else:
        x_svd_train = np.empty((train_text_matrix.shape[0], 0))
        x_svd_valid = np.empty((valid_text_matrix.shape[0], 0))

    feature_names = x_meta_train.columns.tolist() + [f"title_svd_{i}" for i in range(x_svd_train.shape[1])]
    x_boost_train = pd.DataFrame(
        np.hstack([x_meta_train_scaled, x_svd_train]),
        columns=feature_names,
        index=train_df.index,
    )
    x_boost_valid = pd.DataFrame(
        np.hstack([x_meta_valid_scaled, x_svd_valid]),
        columns=feature_names,
        index=valid_df.index,
    )
    return x_boost_train, x_boost_valid, feature_names


def preview_transformed_features(df: pd.DataFrame, rows: int = 5) -> None:
    FEATURE_PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    preview_rows = min(rows, len(df))

    cleaned_preview = pd.DataFrame(
        {
            ID_COL: df[ID_COL],
            LABEL_COL: df[LABEL_COL],
            "title_raw": df["title"],
            "title_clean": df["title"].map(clean_text),
            "venue_raw": df["venue"],
            "venue_clean": df["venue"].map(clean_text),
            "authors_raw": df["authors"],
            "authors_parsed": df["authors"].map(parse_authors).map(lambda values: " | ".join(values)),
            "doi_raw": df["doi"],
            "doi_prefix": df["doi"].map(doi_prefix),
            "doi_suffix_head": df["doi"].map(doi_suffix_head),
            "doi_suffix_head_missing": df["doi"].map(doi_suffix_head).eq("").astype(int),
        }
    )

    metadata_builder = MetadataBuilder(rare_threshold=2)
    metadata = metadata_builder.fit_transform(df)

    text_vectorizer = make_text_vectorizer()
    title_tfidf = text_vectorizer.fit_transform(df["title"].fillna(""))
    tfidf_names = text_vectorizer.get_feature_names_out()

    cleaned_preview.head(preview_rows).to_csv(
        FEATURE_PREVIEW_DIR / "cleaned_preview_head.csv",
        index=False,
    )
    metadata.head(preview_rows).to_csv(
        FEATURE_PREVIEW_DIR / "metadata_features_head.csv",
        index=False,
    )

    top_term_rows = []
    for row_idx in range(preview_rows):
        row = title_tfidf.getrow(row_idx)
        if row.nnz == 0:
            top_term_rows.append(
                {
                    "row": row_idx,
                    ID_COL: df.iloc[row_idx][ID_COL],
                    LABEL_COL: df.iloc[row_idx][LABEL_COL],
                    "term": "",
                    "tfidf": 0.0,
                }
            )
            continue

        order = np.argsort(row.data)[-12:][::-1]
        for pos in order:
            feature_idx = row.indices[pos]
            top_term_rows.append(
                {
                    "row": row_idx,
                    ID_COL: df.iloc[row_idx][ID_COL],
                    LABEL_COL: df.iloc[row_idx][LABEL_COL],
                    "term": tfidf_names[feature_idx],
                    "tfidf": row.data[pos],
                }
            )

    top_terms = pd.DataFrame(top_term_rows)
    top_terms.to_csv(FEATURE_PREVIEW_DIR / "title_tfidf_top_terms_head.csv", index=False)

    summary = pd.DataFrame(
        [
            {"feature_block": "cleaned_text_preview", "rows": len(cleaned_preview), "columns": cleaned_preview.shape[1]},
            {"feature_block": "metadata_features", "rows": metadata.shape[0], "columns": metadata.shape[1]},
            {"feature_block": "title_tfidf", "rows": title_tfidf.shape[0], "columns": title_tfidf.shape[1]},
            {"feature_block": "title_tfidf_nonzero", "rows": title_tfidf.nnz, "columns": np.nan},
        ]
    )
    summary.to_csv(FEATURE_PREVIEW_DIR / "feature_preview_summary.csv", index=False)

    report_lines = [
        "# Feature Preview Before Classifier Fit",
        "",
        "This preview is generated for inspection only. It is not reused by CV training, so it does not change validation behavior.",
        "",
        "## Feature Block Summary",
        "",
        "```text",
        summary.to_string(index=False),
        "```",
        "",
        "## Cleaned Raw Fields",
        "",
        "```text",
        cleaned_preview.head(preview_rows).to_string(index=False),
        "```",
        "",
        "## Metadata Features",
        "",
        "```text",
        metadata.head(preview_rows).to_string(index=False),
        "```",
        "",
        "## Top Title TF-IDF Terms",
        "",
        "```text",
        top_terms.to_string(index=False),
        "```",
    ]
    (FEATURE_PREVIEW_DIR / "feature_preview_report.md").write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    print("\nFeature preview before classifier fit")
    print("-------------------------------------")
    print(summary.to_string(index=False))
    print("\nCleaned fields preview:")
    print(
        cleaned_preview[
            [
                ID_COL,
                LABEL_COL,
                "title_clean",
                "venue_clean",
                "authors_parsed",
                "doi_prefix",
                "doi_suffix_head",
                "doi_suffix_head_missing",
            ]
        ]
        .head(preview_rows)
        .to_string(index=False)
    )
    print("\nMetadata features preview:")
    print(metadata.head(preview_rows).to_string(index=False))
    print("\nTop title TF-IDF terms preview:")
    print(top_terms.to_string(index=False))
    print(f"\nFeature preview files written to: {FEATURE_PREVIEW_DIR}")


def run_cv(
    df: pd.DataFrame,
    n_splits: int,
    svd_components: int,
) -> tuple[pd.DataFrame, pd.DataFrame, str, dict[str, float]]:
    y_raw = df[LABEL_COL].to_numpy()
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    all_classes = np.arange(len(label_encoder.classes_))

    splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    oof_proba = np.zeros((len(df), len(all_classes)), dtype=float)
    base_oof_proba = {
        "logistic_elasticnet": np.zeros((len(df), len(all_classes)), dtype=float),
        "calibrated_linear_svc": np.zeros((len(df), len(all_classes)), dtype=float),
        "chi2_linear_svc": np.zeros((len(df), len(all_classes)), dtype=float),
        "boosting": np.zeros((len(df), len(all_classes)), dtype=float),
    }
    oof_pred = np.zeros(len(df), dtype=int)
    rows = []
    boosting_name = "not_run"

    for fold, (train_idx, valid_idx) in enumerate(splitter.split(df, y), start=1):
        train_df = df.iloc[train_idx].reset_index(drop=True)
        valid_df = df.iloc[valid_idx].reset_index(drop=True)
        y_train = y[train_idx]
        y_valid = y[valid_idx]

        text_vectorizer = make_text_vectorizer()
        x_text_train = text_vectorizer.fit_transform(train_df["title"].fillna(""))
        x_text_valid = text_vectorizer.transform(valid_df["title"].fillna(""))

        logistic = make_logistic()
        logistic.fit(x_text_train, y_train)
        prob_logistic = predict_aligned_proba(
            logistic, x_text_valid, logistic.classes_, all_classes
        )
        base_oof_proba["logistic_elasticnet"][valid_idx] = prob_logistic

        svm = make_svm()
        svm.fit(x_text_train, y_train)
        prob_svm = predict_aligned_proba(svm, x_text_valid, svm.classes_, all_classes)
        base_oof_proba["calibrated_linear_svc"][valid_idx] = prob_svm

        chi2 = AdditiveChi2Sampler(sample_steps=2)
        x_chi2_train = chi2.fit_transform(x_text_train)
        x_chi2_valid = chi2.transform(x_text_valid)
        chi2_svm = make_chi2_svm()
        chi2_svm.fit(x_chi2_train, y_train)
        prob_chi2_svm = predict_aligned_proba(
            chi2_svm, x_chi2_valid, chi2_svm.classes_, all_classes
        )
        base_oof_proba["chi2_linear_svc"][valid_idx] = prob_chi2_svm

        x_boost_train, x_boost_valid, _ = build_dense_boost_features(
            train_df, valid_df, x_text_train, x_text_valid, svd_components
        )
        boosting, boosting_name = make_boosting_model()
        boosting.fit(x_boost_train, y_train)
        prob_boost = predict_aligned_proba(
            boosting, x_boost_valid, boosting.classes_, all_classes
        )
        base_oof_proba["boosting"][valid_idx] = prob_boost

        weights = {
            "logistic": 0.35,
            "svm": 0.20,
            "chi2_svm": 0.30,
            boosting_name: 0.15,
        }
        prob_ensemble = (
            weights["logistic"] * prob_logistic
            + weights["svm"] * prob_svm
            + weights["chi2_svm"] * prob_chi2_svm
            + weights[boosting_name] * prob_boost
        )
        pred_ensemble = prob_ensemble.argmax(axis=1)

        oof_proba[valid_idx] = prob_ensemble
        oof_pred[valid_idx] = pred_ensemble

        rows.extend(
            [
                {
                    "fold": fold,
                    "model": "logistic_elasticnet",
                    "macro_f1": f1_score(y_valid, prob_logistic.argmax(axis=1), average="macro"),
                },
                {
                    "fold": fold,
                    "model": "calibrated_linear_svc",
                    "macro_f1": f1_score(y_valid, prob_svm.argmax(axis=1), average="macro"),
                },
                {
                    "fold": fold,
                    "model": "chi2_linear_svc",
                    "macro_f1": f1_score(
                        y_valid, prob_chi2_svm.argmax(axis=1), average="macro"
                    ),
                },
                {
                    "fold": fold,
                    "model": f"boosting_{boosting_name}",
                    "macro_f1": f1_score(y_valid, prob_boost.argmax(axis=1), average="macro"),
                },
                {
                    "fold": fold,
                    "model": "weighted_ensemble",
                    "macro_f1": f1_score(y_valid, pred_ensemble, average="macro"),
                },
            ]
        )
        print(
            f"fold={fold} ensemble_macro_f1="
            f"{f1_score(y_valid, pred_ensemble, average='macro'):.5f}"
        )

    best_weights, tuned_proba, tuned_pred, tuned_score = tune_oof_weights(
        y, base_oof_proba
    )
    rows.append(
        {
            "fold": "oof",
            "model": "tuned_weighted_ensemble",
            "macro_f1": tuned_score,
        }
    )

    scores = pd.DataFrame(rows)
    decoded_pred = label_encoder.inverse_transform(tuned_pred)
    oof = df[[ID_COL, LABEL_COL]].copy()
    oof["pred_label"] = decoded_pred
    for model_name, probs in base_oof_proba.items():
        for pos, label in enumerate(label_encoder.classes_):
            oof[f"{model_name}_prob_{label}"] = probs[:, pos]
    for pos, label in enumerate(label_encoder.classes_):
        oof[f"tuned_ensemble_prob_{label}"] = tuned_proba[:, pos]

    report = classification_report(y_raw, decoded_pred)
    cm = pd.DataFrame(
        confusion_matrix(y_raw, decoded_pred, labels=label_encoder.classes_),
        index=[f"true_{label}" for label in label_encoder.classes_],
        columns=[f"pred_{label}" for label in label_encoder.classes_],
    )
    cm.to_csv(OUTPUT_DIR / "confusion_matrix.csv")
    (OUTPUT_DIR / "best_oof_weights.txt").write_text(
        "\n".join([f"{key}: {value:.2f}" for key, value in best_weights.items()]),
        encoding="utf-8",
    )
    return scores, oof, report, best_weights


def tune_oof_weights(
    y_true: np.ndarray,
    base_oof_proba: dict[str, np.ndarray],
    step: float = 0.05,
) -> tuple[dict[str, float], np.ndarray, np.ndarray, float]:
    model_names = list(base_oof_proba)
    best_score = -1.0
    best_weights = {name: 0.0 for name in model_names}
    best_proba = base_oof_proba[model_names[0]]
    best_pred = best_proba.argmax(axis=1)

    total_units = int(round(1.0 / step))

    def generate_weight_units(n_models: int, remaining: int) -> list[list[int]]:
        if n_models == 1:
            return [[remaining]]

        combos = []
        for value in range(remaining + 1):
            for tail in generate_weight_units(n_models - 1, remaining - value):
                combos.append([value, *tail])
        return combos

    for units in generate_weight_units(len(model_names), total_units):
        weights = np.array(units, dtype=float) / total_units
        proba = sum(
            weight * base_oof_proba[name]
            for weight, name in zip(weights, model_names)
        )
        pred = proba.argmax(axis=1)
        score = f1_score(y_true, pred, average="macro")
        if score > best_score:
            best_score = score
            best_proba = proba
            best_pred = pred
            best_weights = {
                name: float(weight) for name, weight in zip(model_names, weights)
            }

    return best_weights, best_proba, best_pred, best_score


def write_markdown_summary(
    scores: pd.DataFrame,
    report: str,
    n_splits: int,
    best_weights: dict[str, float],
) -> None:
    mean_scores = (
        scores.groupby("model")["macro_f1"]
        .agg(["mean", "std"])
        .sort_values("mean", ascending=False)
        .reset_index()
    )

    lines = [
        "# Ensemble Experiment Summary",
        "",
        "## Goal",
        "",
        "Validate the first ensemble pipeline inside `soi_vng` only.",
        "",
        "## Data Loading",
        "",
        f"- Train file: `{TRAIN_PATH.as_posix()}`",
        f"- CV: Stratified K-Fold with `{n_splits}` folds",
        "- Metric: `macro_f1`",
        "",
        "## Feature Engineering",
        "",
        "- `title`: word TF-IDF 1-2 grams plus char TF-IDF 3-5 grams.",
        "- `venue`: cleaned categorical feature with rare bucket.",
        "- `authors`: kept in preview only; excluded from model features to reduce memorization risk.",
        "- `year`: normalized year, missing flag and paper age.",
        "- `doi`: has DOI, length, digit/slash/dot counts, rare-bucketed DOI prefix, and DOI suffix head.",
        "- `title` TF-IDF is reduced with TruncatedSVD before feeding the boosting model.",
        "",
        "## Model Training",
        "",
        "- Model A: Logistic Regression ElasticNet on full sparse title TF-IDF.",
        "- Model B: Calibrated LinearSVC on full sparse title TF-IDF.",
        "- Model C: AdditiveChi2Sampler + Calibrated LinearSVC on title TF-IDF.",
        "- Model D: LightGBM if installed, otherwise scikit-learn HistGradientBoosting.",
        "- Ensemble: weighted soft voting with weights `0.35 / 0.20 / 0.30 / 0.15`.",
        "- OOF-tuned ensemble: grid search over base model probabilities with step `0.05`.",
        "",
        "## Evaluation",
        "",
        "```text",
        mean_scores.to_string(index=False),
        "```",
        "",
        "## Best OOF Weights",
        "",
        "```text",
        "\n".join([f"{key}: {value:.2f}" for key, value in best_weights.items()]),
        "```",
        "",
        "Interpretation: keep a base model only when it improves OOF macro F1. If a weight is `0.00`, that model is currently hurting or not adding useful diversity.",
        "",
        "## Classification Report",
        "",
        "```text",
        report,
        "```",
        "",
        "## Output Files",
        "",
        "- `cv_scores.csv`: fold-level score for every model.",
        "- `oof_predictions.csv`: out-of-fold prediction and probability columns.",
        "- `confusion_matrix.csv`: confusion matrix from ensemble OOF predictions.",
        "- `submission_hieu_<number>.csv`: test prediction using full-train models and the best OOF weights.",
        "- `test_probabilities.csv`: test probabilities from the tuned ensemble.",
        "",
        "## Next Experiment",
        "",
        "- Install LightGBM/XGBoost/CatBoost to compare real boosting models instead of the fallback booster.",
        "- Improve metadata model before giving it non-zero ensemble weight.",
        "- Add per-class error analysis for labels with weakest F1.",
    ]
    (OUTPUT_DIR / "experiment_summary.md").write_text("\n".join(lines), encoding="utf-8")


def next_submission_path() -> Path:
    existing_numbers = []
    for path in OUTPUT_DIR.glob("submission_hieu_*.csv"):
        match = re.fullmatch(r"submission_hieu_(\d+)\.csv", path.name)
        if match:
            existing_numbers.append(int(match.group(1)))

    next_number = max(existing_numbers, default=0) + 1
    return OUTPUT_DIR / f"submission_hieu_{next_number}.csv"


def train_full_and_predict_test(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    best_weights: dict[str, float],
    svd_components: int,
) -> None:
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(train_df[LABEL_COL].to_numpy())
    all_classes = np.arange(len(label_encoder.classes_))

    text_vectorizer = make_text_vectorizer()
    x_text_train = text_vectorizer.fit_transform(train_df["title"].fillna(""))
    x_text_test = text_vectorizer.transform(test_df["title"].fillna(""))

    logistic = make_logistic()
    logistic.fit(x_text_train, y)
    prob_logistic = predict_aligned_proba(logistic, x_text_test, logistic.classes_, all_classes)

    svm = make_svm()
    svm.fit(x_text_train, y)
    prob_svm = predict_aligned_proba(svm, x_text_test, svm.classes_, all_classes)

    chi2 = AdditiveChi2Sampler(sample_steps=2)
    x_chi2_train = chi2.fit_transform(x_text_train)
    x_chi2_test = chi2.transform(x_text_test)
    chi2_svm = make_chi2_svm()
    chi2_svm.fit(x_chi2_train, y)
    prob_chi2_svm = predict_aligned_proba(
        chi2_svm, x_chi2_test, chi2_svm.classes_, all_classes
    )

    x_boost_train, x_boost_test, _ = build_dense_boost_features(
        train_df, test_df, x_text_train, x_text_test, svd_components
    )
    boosting, boosting_name = make_boosting_model()
    boosting.fit(x_boost_train, y)
    prob_boost = predict_aligned_proba(boosting, x_boost_test, boosting.classes_, all_classes)

    probs_by_name = {
        "logistic_elasticnet": prob_logistic,
        "calibrated_linear_svc": prob_svm,
        "chi2_linear_svc": prob_chi2_svm,
        "boosting": prob_boost,
    }
    tuned_proba = sum(best_weights[name] * probs for name, probs in probs_by_name.items())
    pred = label_encoder.inverse_transform(tuned_proba.argmax(axis=1))

    submission = pd.DataFrame({ID_COL: test_df[ID_COL], LABEL_COL: pred})
    numbered_submission_path = next_submission_path()
    submission.to_csv(numbered_submission_path, index=False)

    probabilities = pd.DataFrame({ID_COL: test_df[ID_COL]})
    for pos, label in enumerate(label_encoder.classes_):
        probabilities[f"prob_{label}"] = tuned_proba[:, pos]
    probabilities["pred_label"] = pred
    probabilities.to_csv(OUTPUT_DIR / "test_probabilities.csv", index=False)

    model_note = [
        "# Submission Note",
        "",
        f"- Test file: `{TEST_PATH.as_posix()}`",
        f"- Booster used: `{boosting_name}`",
        f"- Submission file: `{numbered_submission_path.name}`",
        "- Probability file: `test_probabilities.csv`",
        "",
        "## Weights",
        "",
        "```text",
        "\n".join([f"{key}: {value:.2f}" for key, value in best_weights.items()]),
        "```",
    ]
    (OUTPUT_DIR / "submission_note.md").write_text("\n".join(model_note), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--svd-components", type=int, default=120)
    parser.add_argument("--preview-rows", type=int, default=5)
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(TRAIN_PATH)
    preview_transformed_features(df, rows=args.preview_rows)

    scores, oof, report, best_weights = run_cv(
        df, n_splits=args.folds, svd_components=args.svd_components
    )
    scores.to_csv(OUTPUT_DIR / "cv_scores.csv", index=False)
    oof.to_csv(OUTPUT_DIR / "oof_predictions.csv", index=False)
    write_markdown_summary(scores, report, n_splits=args.folds, best_weights=best_weights)

    if TEST_PATH.exists():
        test_df = pd.read_csv(TEST_PATH)
        train_full_and_predict_test(df, test_df, best_weights, args.svd_components)

    print("\nMean CV scores:")
    print(
        scores.groupby("model")["macro_f1"]
        .agg(["mean", "std"])
        .sort_values("mean", ascending=False)
        .to_string()
    )
    print("\nBest OOF weights:")
    for model_name, weight in best_weights.items():
        print(f"{model_name}: {weight:.2f}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
