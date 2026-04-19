# SciBERT Classifier Experiment

## Goal

Fine-tune SciBERT directly as a sequence classifier on structured text without authors.

## Structured Text

```text
title: <clean_title> [SEP] venue: <clean_venue> [SEP] year: <year> [SEP] doi publisher: <doi_prefix> [SEP] doi source: <doi_suffix_head_or_none>
```

## Model

- Model: `allenai/scibert_scivocab_uncased`
- Epochs per fold: `4`
- Full-train epochs: `4`
- Learning rate: `2e-05`
- Weight decay: `0.01`
- Batch size: `8`
- Max length: `160`

## CV Scores

```text
 fold                       model  macro_f1
    1 scibert_sequence_classifier  0.243097
    2 scibert_sequence_classifier  0.318390
    3 scibert_sequence_classifier  0.208023
    4 scibert_sequence_classifier  0.253182
    5 scibert_sequence_classifier  0.200974

mean_macro_f1 = 0.244733
std_macro_f1  = 0.046802
```

## Classification Report

```text
              precision    recall  f1-score   support

           1       0.36      0.52      0.43       130
           2       0.32      0.37      0.34       103
           3       0.00      0.00      0.00        85
           4       0.06      0.01      0.02        89
           5       0.34      0.62      0.44       103

    accuracy                           0.34       510
   macro avg       0.22      0.30      0.25       510
weighted avg       0.24      0.34      0.27       510

```

## Output Files

- `structured_text_train.csv`
- `structured_text_test.csv`
- `cv_scores.csv`
- `oof_predictions.csv`
- `confusion_matrix.csv`
- `test_probabilities.csv`
- `submission_hieu_scibert_2.csv`