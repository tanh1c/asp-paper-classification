# Current Ensemble Workflow

## Status Check

The current pipeline includes the requested core parts:

- `title` text cleaning before TF-IDF.
- Word TF-IDF with English stopword removal.
- Character TF-IDF kept without stopword removal.
- Additive Chi-square kernel approximation for a title-only SVM branch.
- Metadata features from `venue`, `year`, and `doi`; `authors` is kept for preview only.
- DOI split into `doi_prefix` and `doi_suffix_head`.
- Soft voting with fixed weights.
- OOF-tuned soft voting that searches weights by validation `macro_f1`.
- Numbered submission output as `submission_hieu_<number>.csv`.

Current feature sizes from the latest preview:

```text
cleaned_text_preview: 510 rows x 12 columns
metadata_features:    510 rows x 74 columns
title_tfidf:          510 rows x 17365 columns
title_tfidf_nonzero:  84230 non-zero values
```

Latest tuned OOF weights:

```text
logistic_elasticnet: 0.85
calibrated_linear_svc: 0.00
chi2_linear_svc: 0.00
boosting: 0.15
```

Interpretation: the architecture has the Chi2 kernel branch, but the latest OOF tuning does not give it weight yet. Logistic title TF-IDF remains the main model, while the metadata/SVD boosting branch contributes a small amount.

## Architecture

Rendered PNG:

![Current Architecture](workflow_diagrams/current_architecture.png)

```mermaid
flowchart TD
    A[Raw train CSV] --> B[Stratified K-Fold]
    A2[Raw test CSV] --> T0[Full-train prediction path]

    B --> C1[Train fold]
    B --> C2[Validation fold]

    C1 --> D1[Clean title]
    C2 --> D2[Clean title]
    T0 --> D3[Clean title]

    D1 --> E1[Word TF-IDF 1-2 grams<br/>stop_words=english]
    D1 --> E2[Char TF-IDF 3-5 grams]
    D2 --> E1V[Transform word TF-IDF]
    D2 --> E2V[Transform char TF-IDF]

    E1 --> F[Title TF-IDF sparse matrix]
    E2 --> F
    E1V --> FV[Validation title TF-IDF]
    E2V --> FV

    F --> M1[Logistic Regression ElasticNet]
    FV --> P1[Logistic probabilities]
    M1 --> P1

    F --> M2[Calibrated LinearSVC]
    FV --> P2[LinearSVC probabilities]
    M2 --> P2

    F --> K1[AdditiveChi2Sampler]
    FV --> K2[AdditiveChi2Sampler transform]
    K1 --> M3[Calibrated LinearSVC]
    K2 --> P3[Chi2-SVC probabilities]
    M3 --> P3

    C1 --> G1[MetadataBuilder fit]
    C2 --> G2[MetadataBuilder transform]
    G1 --> H1[Metadata features]
    G2 --> H2[Validation metadata features]
    F --> S1[TruncatedSVD title features]
    FV --> S2[TruncatedSVD validation features]
    H1 --> J1[Scale metadata + concat SVD]
    S1 --> J1
    H2 --> J2[Scale metadata + concat SVD]
    S2 --> J2
    J1 --> M4[LightGBM if installed<br/>else HistGradientBoosting]
    J2 --> P4[Boosting probabilities]
    M4 --> P4

    P1 --> V1[Fixed soft voting]
    P2 --> V1
    P3 --> V1
    P4 --> V1

    P1 --> V2[OOF tuned soft voting]
    P2 --> V2
    P3 --> V2
    P4 --> V2

    V1 --> R1[Fold macro_f1]
    V2 --> R2[OOF macro_f1 + best weights]
    R2 --> O1[best_oof_weights.txt]
    R2 --> O2[oof_predictions.csv]
    R2 --> O3[confusion_matrix.csv]
```

## Feature Flow

Rendered PNG:

![Feature Flow](workflow_diagrams/feature_flow.png)

```mermaid
flowchart LR
    A[title] --> A1[clean_text]
    A1 --> A2[Word TF-IDF<br/>1-2 grams<br/>English stopwords removed]
    A1 --> A3[Char TF-IDF<br/>3-5 grams]
    A2 --> A4[Full sparse title TF-IDF]
    A3 --> A4
    A4 --> A5[Logistic ElasticNet]
    A4 --> A6[LinearSVC]
    A4 --> A7[AdditiveChi2Sampler + LinearSVC]
    A4 --> A8[TruncatedSVD for boosting]

    B[venue] --> B1[clean_text]
    B1 --> B2[rare bucket]
    B2 --> B3[one-hot]

    D[year] --> D1[year_normalized]
    D --> D2[paper_age]
    D --> D3[year_is_missing]

    E[doi] --> E1[doi_prefix]
    E --> E2[doi_suffix_head]
    E --> E3[doi_suffix_head_missing]
    E --> E4[length/count features]
    E1 --> E5[rare bucket + one-hot]
    E2 --> E6[rare bucket + one-hot]

    B3 --> Z[Metadata matrix]
    D1 --> Z
    D2 --> Z
    D3 --> Z
    E3 --> Z
    E4 --> Z
    E5 --> Z
    E6 --> Z

    Z --> Z1[StandardScaler]
    A8 --> Z2[Concat metadata + title SVD]
    Z1 --> Z2
    Z2 --> Z3[Boosting model]
```

## Current Feature Coverage

The current feature set is enough for a solid first ensemble experiment:

- Strong title branch: full sparse TF-IDF into Logistic/SVC.
- Kernel-style title branch: `AdditiveChi2Sampler + LinearSVC`.
- Metadata branch: compact venue/year/DOI features plus title SVD into boosting.
- DOI has both publisher-level signal and suffix/event-like signal.
- Missingness is represented for `year` and DOI suffix head.

The main limitation is not missing feature coverage, but model contribution: the latest OOF tuning still trusts mostly Logistic. That means the next useful work is not adding many more raw features, but improving the non-Logistic branches until they add real diversity.

## Next Checks

- Try `rare_threshold` values `2`, `3`, `5`, and `10`.
- Try Logistic Hybrid: full title TF-IDF plus metadata one-hot/numeric features.
- Tune `C` for `LinearSVC` and `chi2_linear_svc`.
- Compare stopword removal on/off because it changed the Logistic score.
- Install real LightGBM/XGBoost/CatBoost if the environment supports them.
