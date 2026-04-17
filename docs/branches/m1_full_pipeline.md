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

## Phase 3 experiment result

- Phase 3 winner: `exp_m1_002`
- Candidate tốt nhất: `word12_binary_c6`
- Hướng tốt nhất hiện tại: `text_tuned_binary`
- Model đã khóa sau Phase 3: `TF word presence (1,2) + OneVsRest Logistic Regression`
- CV Macro F1: `0.334261`
- CV std: `0.041403`
- Cải thiện so với Phase 2: `+0.007234`
- Submission mới: `data/submissions/sub_m1_v2_phase3_best.csv`

## Backup candidate đáng giữ lại

- Run ID: `exp_m1_011`
- Candidate: `word12_tfidf_c2_min2`
- CV Macro F1: `0.330420`
- CV std: `0.023573`
- Ý nghĩa: thấp điểm hơn winner nhưng ổn định hơn, phù hợp làm backup nếu Phase 4 cần cân bằng giữa mean và variance

## Insight sau Phase 3

- Hướng tốt nhất của M1 vẫn là `text-first`, nhưng không phải TF-IDF chuẩn mà là `binary word presence`.
- Metadata token augmentation và hybrid sparse chưa giúp vượt text tuned.
- Tăng `ngram` lên `(1,3)` hoặc chuyển hẳn sang char model đều không mang lại lợi ích thực sự.
- Nếu tiếp tục tối ưu ở Phase 4, M1 nên đi theo:
  - fine-tune quanh `binary word (1,2)`
  - thử thêm 1-2 biến thể ensemble nhỏ quanh nhóm text-only mạnh nhất
  - chỉ quay lại hybrid nếu có một giả thuyết feature rất cụ thể

## Artifact của Phase 3

- Kết quả đầy đủ: `reports/battle_m1/phase3_results.csv`
- Tóm tắt phase: `reports/battle_m1/phase3_experiment_summary.md`
- Audit log: `reports/battle_m1/audit_log.md`
