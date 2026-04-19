# Ensemble Feature Plan

## 1. Goal

Build a paper classification pipeline that combines text features, metadata features, and ensemble models. Initial feature priority:

```text
title > venue ~= doi > year
```

Interpretation:

- `title` is the main signal source.
- `venue` can be a strong signal if train and test have similar conference or journal distributions.
- `authors` can help, but it has high overfitting risk; keep it out of the main model unless validation proves it helps.
- `year` is a secondary feature that can capture time-based trends.
- `doi` should not be used too strongly as raw text; it should be split into lightweight derived features.

## 2. Data Splitting And Validation

Use the same validation strategy for all models so the comparison stays fair.

Rules:

- Split train/validation with Stratified K-Fold.
- Main metric: `macro_f1`.
- Every feature encoder, TF-IDF vectorizer, SVD transformer, scaler, and model must be fitted inside each fold.
- Do not compute frequency features, target signals, vocabulary, or encoders on the full dataset before splitting.

Correct pipeline:

```text
raw train
-> split fold
-> fit preprocessing on train fold
-> transform train fold and validation fold
-> train model
-> predict validation fold
-> compute macro_f1
```

## 3. Title Features

`title` is the most important feature, so preprocessing should be light enough to preserve domain-specific scientific terms.

Recommended:

- Lowercase text.
- Normalize whitespace.
- Remove noisy characters only when needed.
- Keep scientific keywords, abbreviations, and meaningful phrases.
- Use word TF-IDF with 1-2 grams.
- Optionally add char TF-IDF with 3-5 grams if titles contain many abbreviations, spelling variations, or acronyms.

Avoid overly aggressive cleaning:

- Do not stem or lemmatize until validation proves it helps.
- Do not remove words such as `using`, `based`, `via`, or `towards` too early, because they can still encode useful title patterns.

Suggested title features:

```text
title_clean
title_word_count
title_char_count
title_avg_word_length
title_has_colon
title_has_question
title_tfidf_word_1_2
title_tfidf_char_3_5
```

## 4. Venue Features

`venue` should be used as both a categorical feature and a frequency feature.

Suggested features:

```text
venue_clean
venue_is_missing
venue_frequency
venue_count_in_train_fold
venue_tfidf_or_onehot
```

Notes:

- If using `venue_frequency`, compute it only on the train fold.
- If there are too many rare venue values, group low-frequency venues into `__rare__`.
- Do not use label distribution by venue unless target encoding is implemented with strict cross-validation, because it can easily create leakage.

## 5. Author Policy

`authors` can carry useful signal, but it can overfit easily in this small dataset. The current pipeline keeps authors for preview/EDA only and excludes author-derived features from model fitting.

Current usage:

```text
authors_raw -> preview only
authors_parsed -> preview only
authors_is_missing -> preview only
```

Rules:

- Parse authors into a list of names.
- Normalize with lowercase and whitespace cleanup.
- Do not include author identity or author frequency features in the current model.
- Add author-derived features only if a future validation experiment proves they improve OOF macro F1 without overfitting.

## 6. Year Features

`year` is a secondary feature. The model should not depend on it too heavily.

Suggested features:

```text
year
year_is_missing
year_normalized
year_bucket
paper_age
```

Normalization:

```text
year_normalized = (year - mean_train_year) / std_train_year
paper_age = max_train_year - year
```

Notes:

- Mean and standard deviation must be computed on the train fold.
- If `year` is missing, add a `year_is_missing` flag.

## 7. DOI Features

DOI should be used as auxiliary metadata, not as a raw ID-like text feature.

Suggested features:

```text
has_doi
doi_length
doi_prefix
doi_digit_count
doi_slash_count
doi_dot_count
```

Notes:

- `doi_prefix` can help because some publishers or venues may correlate with labels.
- If `doi_prefix` is too rare, group it into `__rare__`.
- Do not let the model memorize the full raw DOI when the dataset is small.

## 8. Boosting Features

Compact features for LightGBM, XGBoost, and CatBoost:

```text
year_normalized
paper_age
title_word_count
title_char_count
title_avg_word_length
title_has_colon
title_has_question
venue_frequency
has_doi
doi_length
doi_prefix
doi_digit_count
doi_slash_count
doi_dot_count
```

If text signal is needed in boosting models:

```text
title -> TF-IDF -> TruncatedSVD(100-300 dims) -> boosting model
```

Reasoning:

- Tree boosting is usually not the best choice for very high-dimensional sparse TF-IDF.
- SVD converts TF-IDF into a smaller dense vector.
- Logistic Regression and LinearSVC should still use the full sparse TF-IDF representation.

## 9. Base Models

Start with 4 main models:

```text
Model A: title TF-IDF -> Logistic Regression ElasticNet
Model B: title TF-IDF -> Calibrated LinearSVC
Model C: title TF-IDF -> AdditiveChi2Sampler -> Calibrated LinearSVC
Model D: metadata + SVD(title TF-IDF) -> LightGBM
```

After the baseline is stable, add:

```text
Model E: metadata + SVD(title TF-IDF) -> XGBoost
Model F: metadata + categorical features -> CatBoost
```

Roles:

- Logistic Regression ElasticNet reduces unnecessary features through regularization.
- LinearSVC is usually strong for text classification.
- AdditiveChi2Sampler gives a kernel-style text representation that can help sparse non-negative TF-IDF features.
- LightGBM/XGBoost/CatBoost capture nonlinear relationships in metadata and dense text features.

## 10. Ensemble

Prefer soft voting when models support `predict_proba`. For LinearSVC, use calibration to obtain probabilities.

Initial weights:

```text
0.35 Logistic Regression ElasticNet
0.20 Calibrated LinearSVC
0.30 AdditiveChi2Sampler + Calibrated LinearSVC
0.15 LightGBM
```

Then tune the weights using validation macro F1.

Formula:

```text
final_probability =
    w1 * prob_logistic
  + w2 * prob_svm
  + w3 * prob_chi2_svm
  + w4 * prob_lgbm
```

Final prediction:

```text
final_label = argmax(final_probability)
```

If a model performs poorly on validation or is too similar to another model, reduce its weight or remove it from the ensemble.

## 11. Experiment Order

Follow this order to avoid making the ensemble too complex too early:

```text
1. TF-IDF title + Logistic Regression ElasticNet
2. TF-IDF title + Calibrated LinearSVC
3. TF-IDF title + AdditiveChi2Sampler + Calibrated LinearSVC
4. Metadata-only features + LightGBM
5. SVD(title TF-IDF) + metadata + LightGBM
6. Add XGBoost
7. Add CatBoost
8. Soft voting
9. Tune ensemble weights
10. Per-class error analysis
11. Create submission
```

## 12. Feature Importance

Use multiple methods to evaluate features instead of trusting only one importance score.

For linear models:

```text
high abs(coef_) -> strong feature influence
coef_ close to 0 -> low contribution
```

For boosting models:

```text
feature_importances_
permutation importance
SHAP if there is enough time
```

Check:

- Which features truly improve macro F1.
- Which features increase train score but reduce validation score.
- Which classes are often confused.
- Whether `venue` or `doi` cause overfitting.

## 13. Error Analysis

After each ensemble round, record:

```text
fold score
macro_f1
per-class f1
confusion matrix
top false positives
top false negatives
which feature/model contributes the most
```

Questions to answer:

- Which classes are hardest to distinguish?
- Do errors come from short titles, missing venue, weak DOI signal, or unusual years?
- When does the text model fail while metadata helps?
- Is the boosting model learning `venue` or DOI-derived features too aggressively?

## 14. Final Submission Pipeline

The submission pipeline should be simple but stable:

```text
clean title
-> build title TF-IDF
-> build metadata features
-> train Logistic Regression ElasticNet
-> train Calibrated LinearSVC
-> train AdditiveChi2Sampler + Calibrated LinearSVC
-> train LightGBM metadata + SVD title
-> optionally add XGBoost/CatBoost if validation improves
-> soft voting
-> predict test
-> export submission
```

Add a model to the ensemble only when:

- Validation macro F1 improves.
- Per-class F1 does not drop sharply.
- Its predictions are diverse compared with existing models.
- Error analysis shows the new model fixes mistakes from older models.

## 15. Notebook Notes

Each notebook should contain these Markdown sections:

```text
# Goal
# Data Loading
# Feature Engineering
# Validation Setup
# Model Training
# Evaluation
# Error Analysis
# Next Experiment
```

For each experiment, record:

```text
Hypothesis:
Feature/model change:
Validation result:
What improved:
What got worse:
Next action:
```
