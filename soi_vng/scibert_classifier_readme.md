# SciBERT Classifier Experiment

## Idea

Fine-tune SciBERT directly as a sequence classifier on structured paper text.

Authors are intentionally excluded.

Input format:

```text
title: <clean_title> [SEP] venue: <clean_venue> [SEP] year: <year> [SEP] doi publisher: <doi_prefix> [SEP] doi source: <doi_suffix_head_or_none>
```

Default model:

```text
allenai/scibert_scivocab_uncased
```

## Install

```powershell
python -m pip install torch transformers
```

If CUDA is available, install the matching PyTorch build from the official PyTorch selector instead.

## Run

Full CV plus test submission:

```powershell
python soi_vng\scibert_classifier_experiment.py
```

CV only:

```powershell
python soi_vng\scibert_classifier_experiment.py --skip-test
```

Safer CPU/smaller run:

```powershell
python soi_vng\scibert_classifier_experiment.py --cpu --batch-size 4 --epochs 3 --full-epochs 3
```

## Outputs

Outputs are written to:

```text
soi_vng/scibert_outputs
```

Main files:

- `structured_text_train.csv`
- `structured_text_test.csv`
- `cv_scores.csv`
- `oof_predictions.csv`
- `confusion_matrix.csv`
- `test_probabilities.csv`
- `submission_hieu_scibert_<number>.csv`
- `experiment_summary.md`

## Notes

This is true fine-tuning:

```text
structured text -> SciBERT -> classification head -> logits -> cross entropy loss
```

Unlike the frozen embedding experiment, this updates the SciBERT weights during training, so it can be stronger but can also overfit more easily on 510 rows.
