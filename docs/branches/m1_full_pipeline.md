# M1 Branch Notes

## Branch

- Owner: `M1`
- Branch: `battle/m1-full-pipeline`
- Strategy hiện tại: `text-first`

## Mục tiêu Phase 1

- khóa luật chơi chung cho branch này
- chốt naming cho run và submission đầu tiên
- chuẩn bị nơi ghi report và output
- xác định baseline đầu tiên đủ nhanh, sạch và tái chạy được

## Quyết định hiện tại

- Vẫn dùng rule chung của repo:
  - metric: `Macro F1`
  - CV: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`
- Hướng ưu tiên của M1:
  - dùng `title` làm tín hiệu chính
  - bắt đầu bằng text baseline mạnh, dễ tái tạo
  - chưa đẩy hybrid quá sớm vì benchmark nhanh ban đầu cho thấy text-only đang ổn hơn

## Reserved IDs

- Run ID đầu tiên: `exp_m1_001`
- Submission ID đầu tiên: `sub_m1_001`

## Output của branch

- Audit log theo phase: `reports/battle_m1/audit_log.md`
- Quick EDA report: `reports/battle_m1/quick_eda.md`
- Baseline summary: `reports/battle_m1/phase2_baseline_summary.md`
- Submission đầu tiên: `data/submissions/sub_m1_v1_text_word12_ovr_lr.csv`

## Checklist Phase 1

- [x] branch battle riêng đã được tạo
- [x] branch note đã được tạo
- [x] branch config đã được tạo
- [x] run id và submission id đầu tiên đã được reserve
- [x] baseline hướng text-first đã được chốt để vào Phase 2

## Phase 2 baseline result

- Model đã khóa: `TF-IDF word (1,2) + OneVsRest Logistic Regression`
- CV Macro F1: `0.327027`
- CV std: `0.032543`
- Submission đầu tiên đã tạo: `data/submissions/sub_m1_v1_text_word12_ovr_lr.csv`

## Insight sau Phase 2

- Baseline text-only hiện đang là lựa chọn mở đầu tốt nhất cho M1.
- Quick benchmark ban đầu cho thấy hybrid baseline đơn giản chưa vượt được text-only.
- Phase 3 nên tập trung vào:
  - tuning thêm `C`, `ngram_range`, `min_df`
  - thử char n-gram có kiểm chứng
  - chỉ thêm metadata nếu có cải thiện CV rõ ràng

## Checklist Phase 2

- [x] có script baseline chạy end-to-end
- [x] có quick EDA report
- [x] có CV result đầu tiên
- [x] có submission file đầu tiên
- [x] tracker và submission log đã được cập nhật
- [x] có audit log giải thích lựa chọn kỹ thuật theo phase
