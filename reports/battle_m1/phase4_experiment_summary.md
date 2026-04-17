# Phase 4 Text-Only Optimization Summary - M1

## Branch info

- Owner: M1
- Branch: `battle/m1-full-pipeline`
- Phase 4 focus: continue optimizing around the strongest text-only family

## Goal of this phase

- giữ trọng tâm vào text-only
- kiểm tra xem representation hoặc blend giữa các model text mạnh có giúp tăng điểm không
- chốt candidate tốt nhất cho sprint tiếp theo

## Results

| Run ID | Candidate | Type | Direction | CV Macro F1 | Std |
|---|---|---|---|---:|---:|
| exp_m1_014 | ens_best_backup_50_50 | ensemble | text_only_ensemble | 0.337629 | 0.024355 |
| exp_m1_016 | ens_best_backup_55_45 | ensemble | text_only_ensemble | 0.336599 | 0.030157 |
| exp_m1_015 | ens_best_backup_40_60 | ensemble | text_only_ensemble | 0.333967 | 0.022822 |
| exp_m1_013 | binary_tfidf_c4 | single_model | text_representation_variant | 0.333087 | 0.041163 |
| exp_m1_012 | binary_count_c6 | single_model | text_representation_variant | 0.321457 | 0.027738 |

## Winner of Phase 4

- Run ID: `exp_m1_014`
- Candidate: `ens_best_backup_50_50`
- Type: `ensemble`
- Direction: `text_only_ensemble`
- CV Macro F1: `0.337629`
- CV std: `0.024355`

## Comparison with previous best

- Phase 3 best CV: `0.334261`
- Phase 4 best CV: `0.337629`
- Absolute improvement: `0.003368`

## Submission

- File: `C:/Users/LG/Desktop/Study Material/DataMining/data/submissions/sub_m1_v3_phase4_text_ensemble.csv`

## Short interpretation

- Text-only vẫn là hướng đúng của M1.
- Representation tốt nhất đơn lẻ vẫn là `binary word presence + OVR Logistic Regression`.
- Tuy nhiên blend giữa candidate mạnh nhất và candidate backup ổn định đã cho mean tốt hơn và std thấp hơn, nên Phase 4 winner là một text-only ensemble chứ không phải single model.
