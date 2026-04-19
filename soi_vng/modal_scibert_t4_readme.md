# Modal SciBERT T4 Runner

This runner executes `scibert_classifier_experiment.py` on Modal with:

```text
GPU: T4
RAM: 8192 MB
Timeout: 3 hours
```

## Install Modal Locally

```powershell
python -m pip install modal
modal setup
```

## Run

From the repository root:

```powershell
modal run soi_vng/modal_scibert_t4.py
```

Smaller run:

```powershell
modal run soi_vng/modal_scibert_t4.py --epochs 3 --full-epochs 3 --batch-size 8
```

More conservative memory run:

```powershell
modal run soi_vng/modal_scibert_t4.py --batch-size 4 --max-length 128
```

## Outputs

The remote run writes files into this Modal Volume:

```text
asp-paper-scibert-outputs
```

Expected files:

- `structured_text_train.csv`
- `structured_text_test.csv`
- `cv_scores.csv`
- `oof_predictions.csv`
- `confusion_matrix.csv`
- `test_probabilities.csv`
- `submission_hieu_scibert_<number>.csv`
- `experiment_summary.md`

## Notes

The script uploads only the files needed to run the SciBERT experiment:

- `soi_vng/scibert_classifier_experiment.py`
- `soi_vng/structured_text_embedding_experiment.py`
- `soi_vng/ensemble_experiment.py`
- the full `dataset_stage1/` directory

It does not upload the whole repository.
