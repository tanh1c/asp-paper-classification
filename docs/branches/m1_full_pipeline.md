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

## Phase 4 optimization result

- Phase 4 winner: `exp_m1_014`
- Candidate tốt nhất: `ens_best_backup_50_50`
- Hướng tốt nhất hiện tại: `text_only_ensemble`
- Model đã khóa sau Phase 4:
  - `50% phase3_best_binary_tfidf_c6`
  - `50% phase3_backup_tfidf_min2_c2`
- CV Macro F1: `0.337629`
- CV std: `0.024355`
- Cải thiện so với Phase 3: `+0.003368`
- Submission mới: `data/submissions/sub_m1_v3_phase4_text_ensemble.csv`

## Insight sau Phase 4

- Text-only vẫn là hướng đúng của M1, nhưng best candidate hiện tại đã chuyển từ `single model` sang `ensemble`.
- Blend giữa model mạnh nhất và model backup ổn định vừa tăng mean score vừa giảm variance rất rõ.
- `binary count` không thắng `binary+idf`, nên representation đơn lẻ tốt nhất vẫn là hướng phase 3.
- Nếu tiếp tục tiến tiếp, M1 nên:
  - giữ `exp_m1_014` làm candidate chính
  - giữ `exp_m1_002` làm single-model reference
  - dùng `exp_m1_011` như backup ổn định nếu cần fallback

## Artifact của Phase 4

- Kết quả đầy đủ: `reports/battle_m1/phase4_results.csv`
- Tóm tắt phase: `reports/battle_m1/phase4_experiment_summary.md`
- Audit log: `reports/battle_m1/audit_log.md`

## Phase 5 error analysis result

- So sánh chính:
  - single-model reference: `exp_m1_002`
  - ensemble winner: `exp_m1_014`
- OOF Macro F1:
  - single: `0.337404`
  - ensemble: `0.340033`
- Ensemble sửa đúng thêm: `17` mẫu
- Ensemble làm hỏng so với single: `16` mẫu

## Insight sau Phase 5

- Ensemble vẫn đáng giữ làm candidate chính vì nó cải thiện tổng thể và ổn định hơn.
- Lợi ích rõ nhất nằm ở:
  - Label 1
  - Label 4
- Trade-off lớn nhất là Label 5, nơi single model vẫn nhỉnh hơn đôi chút.
- Các lớp khó nhất hiện tại vẫn là:
  - Label 3
  - Label 4
- Các vùng nhầm lẫn cần tập trung nếu còn tối ưu tiếp:
  - `1 -> 2`
  - `2 -> 1`
  - `4 -> 5`
  - `3 -> 4/5`

## Recommendation sau Phase 5

- Giữ `exp_m1_014` làm candidate chính của M1.
- Giữ `exp_m1_002` làm fallback nếu cần một single model dễ giải thích hơn.
- Nếu làm tiếp phase sau, nên tập trung giảm nhầm lẫn theo cặp lớp thay vì mở rộng thêm hướng feature mới.

## Artifact của Phase 5

- Report chính: `reports/battle_m1/phase5_error_analysis.md`
- OOF predictions: `reports/battle_m1/phase5_cv_predictions.csv`
- Per-class metrics: `reports/battle_m1/phase5_per_class_metrics.csv`
- Confusion matrix:
  - `reports/battle_m1/phase5_confusion_single.csv`
  - `reports/battle_m1/phase5_confusion_ensemble.csv`

## Final showdown sheet

- Main candidate: `exp_m1_014`
- Primary backup: `exp_m1_002`
- Stability reserve: `exp_m1_011`
- Comparison sheet:
  - `reports/battle_m1/final_comparison_sheet.md`
  - `reports/battle_m1/final_comparison_candidates.csv`
