# Structured Text Embedding Experiment

## Goal

Classify papers by converting selected fields into one structured text input, excluding authors.

## Data

- Train file: `C:/project/asp-paper-classification/soi_vng/Stage_1_publcitrain_with_abstract_only.csv`
- Train rows after dropping NaN abstracts: `409`
- Dropped rows with NaN abstract: `101`

## Structured Text Format

```text
title: <clean_title> [SEP] venue: <clean_venue> [SEP] year: <year> [SEP] doi publisher: <doi_prefix> [SEP] doi source: <doi_suffix_head_or_none>
```

## Model

- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Embedding mode: frozen pretrained encoder
- Classifier: `LogisticRegression(C=1.0, class_weight='balanced')`
- Authors: excluded from model input

## CV Result

```text
 fold                         model  macro_f1
    1 structured_embedding_logistic  0.337009
    2 structured_embedding_logistic  0.295167
    3 structured_embedding_logistic  0.259496
    4 structured_embedding_logistic  0.318053
    5 structured_embedding_logistic  0.318765

mean_macro_f1 = 0.305698
std_macro_f1  = 0.029788
```

## Classification Report

```text
              precision    recall  f1-score   support

           1       0.44      0.36      0.40       107
           2       0.35      0.33      0.34        84
           3       0.21      0.21      0.21        66
           4       0.16      0.20      0.18        70
           5       0.40      0.43      0.41        82

    accuracy                           0.32       409
   macro avg       0.31      0.31      0.31       409
weighted avg       0.33      0.32      0.32       409

```

## Output Files

- `structured_text_train.csv`: structured text used for train rows.
- `structured_text_test.csv`: structured text used for test rows.
- `cv_scores.csv`: fold-level scores.
- `oof_predictions.csv`: OOF predictions and probabilities.
- `confusion_matrix.csv`: OOF confusion matrix.
- `test_probabilities.csv`: test probabilities.
- `submission_hieu_embedding_2.csv`: numbered submission from the full-train model.