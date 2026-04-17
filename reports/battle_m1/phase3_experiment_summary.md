# Phase 3 Experiment Summary - M1

## Branch info

- Owner: M1
- Branch: `battle/m1-full-pipeline`
- Strategy at start of phase: `text-first`

## Goal of this phase

- thử nhiều hướng một cách công bằng trên cùng CV
- xác định hướng nào thực sự tốt hơn baseline Phase 2
- chọn ra candidate mạnh nhất để train full và sinh submission mới

## Results

| Run ID | Candidate | Direction | CV Macro F1 | Std |
|---|---|---|---:|---:|
| exp_m1_002 | word12_binary_c6 | text_tuned_binary | 0.334261 | 0.041403 |
| exp_m1_003 | word12_binary_c4 | text_tuned_binary | 0.333087 | 0.041163 |
| exp_m1_004 | word12_binary_c8 | text_tuned_binary | 0.332389 | 0.043238 |
| exp_m1_011 | word12_tfidf_c2_min2 | text_stability_backup | 0.330420 | 0.023573 |
| exp_m1_005 | word13_binary_c6 | text_trigram | 0.326444 | 0.049116 |
| exp_m1_009 | word13_ridge | ridge_text | 0.317129 | 0.038716 |
| exp_m1_008 | word12_svm_none_c05 | linear_svm | 0.316379 | 0.036987 |
| exp_m1_006 | title_venue_binary_c6 | text_plus_metadata_tokens | 0.307499 | 0.034316 |
| exp_m1_007 | hybrid_word13_venue_lr | hybrid_sparse | 0.300849 | 0.029817 |
| exp_m1_010 | char46_lr_c4 | char_model | 0.299349 | 0.032520 |

## Winner of Phase 3

- Run ID: `exp_m1_002`
- Candidate: `word12_binary_c6`
- Direction: `text_tuned_binary`
- Feature set: `title_clean_word12_binary`
- Model: `ovr_logistic_regression`
- CV Macro F1: `0.334261`
- CV std: `0.041403`

## Comparison with Phase 2 baseline

- Phase 2 baseline CV: `0.327027`
- Phase 3 best CV: `0.334261`
- Absolute improvement: `0.007234`

## Submission

- File: `C:/Users/LG/Desktop/Study Material/DataMining/data/submissions/sub_m1_v2_phase3_best.csv`

## Short interpretation

- Tuning quanh hướng text-first vẫn là hướng hiệu quả nhất cho M1.
- Metadata token augmentation và hybrid sparse chưa thắng được text tuned.
- Insight quan trọng nhất của Phase 3 là `binary word presence` đang mạnh hơn TF-IDF chuẩn trên stage 1 hiện tại.
