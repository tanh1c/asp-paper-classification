# Ensemble Experiment Summary

## Goal

Validate the first ensemble pipeline inside `soi_vng` only.

## Data Loading

- Train file: `C:/project/asp-paper-classification/dataset_stage1/Stage_1_publcitrain.csv`
- CV: Stratified K-Fold with `5` folds
- Metric: `macro_f1`

## Feature Engineering

- `title`: word TF-IDF 1-2 grams plus char TF-IDF 3-5 grams.
- `venue`: cleaned categorical feature with rare bucket.
- `authors`: kept in preview only; excluded from model features to reduce memorization risk.
- `year`: normalized year, missing flag and paper age.
- `doi`: has DOI, length, digit/slash/dot counts, rare-bucketed DOI prefix, and DOI suffix head.
- `title` TF-IDF is reduced with TruncatedSVD before feeding the boosting model.

## Model Training

- Model A: Logistic Regression ElasticNet on full sparse title TF-IDF.
- Model B: Calibrated LinearSVC on full sparse title TF-IDF.
- Model C: AdditiveChi2Sampler + Calibrated LinearSVC on title TF-IDF.
- Model D: LightGBM if installed, otherwise scikit-learn HistGradientBoosting.
- Ensemble: weighted soft voting with weights `0.35 / 0.20 / 0.30 / 0.15`.
- OOF-tuned ensemble: grid search over base model probabilities with step `0.05`.

## Evaluation

```text
                          model     mean      std
        tuned_weighted_ensemble 0.328687      NaN
            logistic_elasticnet 0.320574 0.039562
              weighted_ensemble 0.287359 0.050410
boosting_hist_gradient_boosting 0.284567 0.047914
          calibrated_linear_svc 0.279362 0.031401
                chi2_linear_svc 0.256985 0.041770
```

## Best OOF Weights

```text
logistic_elasticnet: 0.85
calibrated_linear_svc: 0.15
chi2_linear_svc: 0.00
boosting: 0.00
```

Interpretation: keep a base model only when it improves OOF macro F1. If a weight is `0.00`, that model is currently hurting or not adding useful diversity.

## Classification Report

```text
              precision    recall  f1-score   support

           1       0.47      0.55      0.51       130
           2       0.27      0.25      0.26       103
           3       0.21      0.18      0.19        85
           4       0.28      0.20      0.23        89
           5       0.40      0.50      0.45       103

    accuracy                           0.36       510
   macro avg       0.33      0.34      0.33       510
weighted avg       0.34      0.36      0.35       510

```

## Output Files

- `cv_scores.csv`: fold-level score for every model.
- `oof_predictions.csv`: out-of-fold prediction and probability columns.
- `confusion_matrix.csv`: confusion matrix from ensemble OOF predictions.
- `submission_hieu_<number>.csv`: test prediction using full-train models and the best OOF weights.
- `test_probabilities.csv`: test probabilities from the tuned ensemble.

## Next Experiment

- Install LightGBM/XGBoost/CatBoost to compare real boosting models instead of the fallback booster.
- Improve metadata model before giving it non-zero ensemble weight.
- Add per-class error analysis for labels with weakest F1.