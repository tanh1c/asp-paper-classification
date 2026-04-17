# Audit Log - Battle M1

File này dùng để ghi lại quyết định kỹ thuật theo từng phase của branch `battle/m1-full-pipeline`.

## Cách dùng từ Phase 3 trở đi

Sau mỗi phase, append thêm một block mới theo cấu trúc:

- mục tiêu phase
- việc đã làm
- kết quả chính
- quyết định đã chốt
- vì sao chọn hướng đó
- hướng bị loại và lý do
- bước tiếp theo

---

## Phase 1 - Setup branch và khóa chiến lược ban đầu

### Mục tiêu

- tạo không gian làm việc riêng cho M1
- khóa luật chơi chung nhưng vẫn giữ branch độc lập
- chốt hướng khởi đầu để sang Phase 2 không bị lan man

### Việc đã làm

- tạo branch `battle/m1-full-pipeline`
- tạo config riêng tại `configs/branches/m1_full_pipeline.yaml`
- tạo note branch tại `docs/branches/m1_full_pipeline.md`
- reserve `run_id = exp_m1_001` và `submission_id = sub_m1_001`
- tạo nơi chứa report riêng cho M1 tại `reports/battle_m1/`

### Quyết định đã chốt

- M1 đi theo hướng `text-first`
- vẫn dùng rule chung:
  - metric `Macro F1`
  - `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`
- baseline đầu tiên phải ưu tiên:
  - nhanh
  - sạch
  - tái chạy được
  - dễ làm mốc so sánh cho các phase sau

### Vì sao chọn `text-first` ngay từ đầu

- Dataset stage 1 nhỏ, trong khi feature text cốt lõi là `title`, nên text baseline có tỷ lệ hiệu quả/công sức rất tốt.
- Metadata hiện tại không quá giàu thông tin:
  - `venue` có ít giá trị
  - `authors` bị thiếu 52 dòng
  - chưa có `abstract`
- Ở giai đoạn sớm, mục tiêu quan trọng nhất là có một pipeline end-to-end thật nhanh để bắt đầu đo điểm.
- Hướng text-first dễ tạo baseline mạnh hơn so với việc đẩy hybrid quá sớm khi chưa biết metadata có thật sự giúp hay không.

### Hướng chưa chọn ở Phase 1 và lý do

- `metadata-first`:
  - chưa ưu tiên vì thiếu `abstract` và metadata hiện tại tương đối mỏng
- `hybrid ngay từ đầu`:
  - chi phí triển khai cao hơn baseline text thuần
  - dễ làm tăng độ phức tạp trước khi có mốc so sánh đơn giản
- `ensemble sớm`:
  - chưa hợp lý khi chưa có model nền đủ tốt

### Bài rút ra

- Với branch battle, điều quan trọng không phải là làm “đủ hết mọi thứ” ngay, mà là khóa một hướng chính đủ rõ để tiến nhanh.
- Có config và note riêng từ đầu giúp branch dễ audit hơn rất nhiều khi sang phase sau.

### Bước tiếp theo

- benchmark nhanh một số baseline nhẹ
- chọn một baseline text đủ tốt để khóa cho Phase 2

---

## Phase 2 - Baseline end-to-end đầu tiên

### Mục tiêu

- có pipeline chạy từ đầu đến cuối
- có CV đầu tiên
- có submission đầu tiên
- có mốc định lượng để biết M1 đang đứng ở đâu

### Việc đã làm

- chạy quick EDA trên train/test stage 1
- benchmark nhanh nhiều baseline text và hybrid nhẹ
- viết script tái chạy được:
  - `scripts/run_m1_phase2_baseline.py`
- sinh:
  - `reports/battle_m1/quick_eda.md`
  - `reports/battle_m1/phase2_baseline_summary.md`
  - `data/submissions/sub_m1_v1_text_word12_ovr_lr.csv`
- cập nhật:
  - `experiments/experiment_tracker.csv`
  - `experiments/submission_log.csv`

### Quan sát dữ liệu rút ra từ quick EDA

- Train: `510` mẫu
- Test: `86` mẫu
- Missing `authors`: `52`
- Duplicate `title` trong train: `2`
- Duplicate `doi` trong train: `18`
- `venue` chủ yếu tập trung vào:
  - `iclp`: `336`
  - `kr`: `174`

### Benchmark đã thử trước khi khóa baseline

#### So sánh text-only với hybrid đơn giản

| Candidate | CV Macro F1 | Std |
|---|---:|---:|
| text + Logistic Regression | 0.321149 | 0.032990 |
| hybrid + Logistic Regression | 0.296451 | 0.058824 |
| hybrid + Linear SVM | 0.082766 | 0.019354 |

#### So sánh các baseline text khác nhau

| Candidate | CV Macro F1 | Std |
|---|---:|---:|
| TF-IDF word (1,2) + Logistic Regression (`lbfgs`) | 0.321149 | 0.032990 |
| TF-IDF char (3,5) + Logistic Regression | 0.287023 | 0.039719 |
| TF-IDF word (1,2) + OneVsRest Logistic Regression (`liblinear`) | 0.327027 | 0.032543 |
| TF-IDF word (1,2) + Linear SVM | 0.304605 | 0.036325 |
| TF-IDF char (3,5) + Linear SVM | 0.270016 | 0.030482 |
| TF-IDF word (1,2) + MultinomialNB | 0.313539 | 0.028902 |
| TF-IDF word + char + OneVsRest Logistic Regression | 0.295655 | 0.048574 |

### Quyết định đã chốt

- baseline chính của Phase 2 là:
  - `TF-IDF word (1,2) + OneVsRest Logistic Regression`
- kết quả chính:
  - CV Macro F1: `0.327027`
  - CV std: `0.032543`
- submission đầu tiên:
  - `sub_m1_v1_text_word12_ovr_lr.csv`

### Vì sao chọn baseline này

- Đây là candidate có CV mean tốt nhất trong nhóm thử nhanh.
- Độ lệch chuẩn vẫn ở mức chấp nhận được với dataset nhỏ.
- Pipeline đơn giản, sạch, dễ tái chạy và dễ giải thích trong báo cáo.
- Hiệu quả tốt hơn hybrid đơn giản ở thời điểm hiện tại, nên giữ được triết lý “đừng tăng độ phức tạp khi chưa có bằng chứng cải thiện”.

### Vì sao chưa chọn các hướng khác

- `char-only`:
  - cho điểm thấp hơn rõ rệt
- `word + char union`:
  - chưa cải thiện, ngược lại còn giảm điểm và tăng variance
- `hybrid baseline`:
  - chưa vượt text-only
  - cho thấy metadata hiện tại chưa tạo ra tín hiệu đủ mạnh ở thiết kế đơn giản
- `Linear SVM`:
  - không thắng OVR Logistic Regression trong benchmark hiện tại
- `Naive Bayes`:
  - nhanh nhưng điểm vẫn thấp hơn candidate đã chọn

### Bài rút ra

- Với stage 1 hiện tại, `title` đúng là tín hiệu mạnh nhất để mở đầu.
- Không phải cứ thêm metadata hoặc feature union là điểm sẽ tăng.
- Benchmark nhỏ nhưng có kiểm soát giúp tránh đi sai hướng rất nhanh.
- OVR Logistic Regression là baseline hợp lý để làm mốc cho các phase tuning tiếp theo.

### Rủi ro còn lại

- Public LB có thể không đi cùng CV hoàn toàn.
- Duplicate `doi` và duplicate `title` cần được để ý thêm ở phase sau.
- Metadata có thể vẫn hữu ích, nhưng cần thiết kế feature hoặc cách kết hợp tốt hơn.

### Bước tiếp theo

- Phase 3 nên tập trung vào:
  - tuning `C`
  - thử `ngram_range` khác
  - kiểm tra `min_df`
  - thử char feature có kiểm soát hơn
  - chỉ quay lại hybrid khi có bằng chứng cải thiện CV
