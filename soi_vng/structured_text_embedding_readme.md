# Structured Text Embedding Experiment

## Idea

This experiment converts selected fields into one structured NLP input and trains a small classifier on frozen pretrained embeddings.

Authors are intentionally excluded.

Input format:

```text
title: <clean_title> [SEP] venue: <clean_venue> [SEP] year: <year> [SEP] doi publisher: <doi_prefix> [SEP] doi source: <doi_suffix_head_or_none>
```

Example:

```text
title: tabled clp for reasoning over stream data. [SEP] venue: iclp [SEP] year: 2016 [SEP] doi publisher: 10.1109 [SEP] doi source: icsc
```

## Install

The current environment needs SentenceTransformers before running this experiment:

```powershell
python -m pip install sentence-transformers
```

## Run

Default lightweight embedding model:

```powershell
python soi_vng\structured_text_embedding_experiment.py
```

Use a scientific-paper-oriented model if available:

```powershell
python soi_vng\structured_text_embedding_experiment.py --model-name allenai-specter
```

Run CV only without creating submission:

```powershell
python soi_vng\structured_text_embedding_experiment.py --skip-test
```

## Outputs

Outputs are written to:

```text
soi_vng/structured_embedding_outputs
```

Main files:

- `structured_text_train.csv`
- `structured_text_test.csv`
- `cv_scores.csv`
- `oof_predictions.csv`
- `confusion_matrix.csv`
- `test_probabilities.csv`
- `submission_hieu_embedding_<number>.csv`
- `experiment_summary.md`
