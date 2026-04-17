# Phase 2 Baseline Summary - M1

## Branch info

- Owner: M1
- Branch: `battle/m1-full-pipeline`
- Strategy: `text-first`

## Baseline selected

- Feature set: `title` only
- Vectorizer: `TF-IDF word (1,2)`
- Model: `OneVsRest Logistic Regression`
- Run ID: `exp_m1_001`
- Submission ID: `sub_m1_001`

## CV result

- Fold scores: [0.330919, 0.388804, 0.306612, 0.307787, 0.301015]
- CV Macro F1 mean: 0.327027
- CV std: 0.032543

## Output

- Submission file: `C:/Users/LG/Desktop/Study Material/DataMining/data/submissions/sub_m1_v1_text_word12_ovr_lr.csv`

## Notes

- Benchmark nhanh trước khi khóa baseline cho thấy text-only đang ổn hơn hybrid baseline đơn giản trên stage 1.
- Đây là baseline đầu tiên của branch M1, ưu tiên tính sạch và khả năng tái chạy.
