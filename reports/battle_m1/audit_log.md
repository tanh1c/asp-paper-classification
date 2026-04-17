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

---

## Phase 3 - Thử nhiều hướng và chọn hướng tốt nhất

### Mục tiêu

- thử nhiều hướng khác nhau nhưng vẫn giữ cùng CV để so sánh công bằng
- tìm xem có hướng nào thắng baseline Phase 2 hay không
- nếu có cải thiện, chốt luôn candidate mạnh nhất cho branch M1

### Việc đã làm

- viết script benchmark có cấu trúc:
  - `scripts/run_m1_phase3_experiments.py`
- thử nhiều hướng lớn:
  - text tuned với `binary word presence`
  - text trigram
  - text + metadata token
  - hybrid sparse
  - Linear SVM
  - Ridge
  - char model
  - một candidate backup thiên về ổn định
- sinh:
  - `reports/battle_m1/phase3_results.csv`
  - `reports/battle_m1/phase3_experiment_summary.md`
  - `data/submissions/sub_m1_v2_phase3_best.csv`
- cập nhật tracker và submission log

### Kết quả đầy đủ của Phase 3

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

### Quyết định đã chốt

- Winner của Phase 3 là:
  - `exp_m1_002`
  - `word12_binary_c6`
- Hướng tốt nhất hiện tại của M1:
  - `text-first` được tune tiếp theo hướng `binary word presence`
- Kết quả chính:
  - Phase 2 baseline: `0.327027`
  - Phase 3 best: `0.334261`
  - Gain: `+0.007234`

### Vì sao chọn hướng này là tốt nhất

- Đây là candidate có `CV mean` cao nhất trong toàn bộ Phase 3.
- Cải thiện là có thật chứ không chỉ xê dịch rất nhỏ quanh baseline.
- Insight kỹ thuật rõ ràng:
  - với stage 1 hiện tại, sự hiện diện của từ (`binary word presence`) có vẻ hữu ích hơn TF-IDF chuẩn
  - title vẫn là tín hiệu mạnh nhất
- Pipeline vẫn còn tương đối đơn giản, nên dễ giữ cho Phase 4 và dễ giải thích trong báo cáo.

### Hướng nào bị loại và vì sao

- `text trigram`:
  - thêm trigram không giúp tăng điểm
  - có dấu hiệu tăng variance
- `text + metadata tokens`:
  - ghép `venue` vào text không giúp vượt baseline text tuned
- `hybrid sparse`:
  - chưa khai thác metadata đủ mạnh để thắng text-only
- `char model`:
  - yếu hơn khá rõ
- `Linear SVM` và `Ridge`:
  - không vượt được logistic tuned

### Insight quan trọng nhất rút ra từ Phase 3

- Hướng đúng của M1 không phải là “hybrid nhiều hơn”, mà là “text-first nhưng tune đúng kiểu”.
- Một thay đổi seemingly nhỏ ở representation (`binary=True`) lại cho hiệu quả hơn hẳn việc thêm metadata hoặc tăng độ phức tạp pipeline.
- Phase 3 cũng cho thấy cần tách bạch:
  - candidate tốt nhất theo mean score
  - candidate backup tốt hơn về độ ổn định

### Backup candidate đáng giữ lại

- `exp_m1_011` không phải winner, nhưng là candidate backup tốt:
  - CV Macro F1: `0.330420`
  - CV std: `0.023573`
- Nếu Phase 4 hoặc Public LB cho thấy candidate winner quá dao động, đây là hướng fallback hợp lý.

### Bài rút ra

- Không nên mặc định metadata sẽ giúp khi dataset còn nhỏ và text đã mang tín hiệu chính.
- Tuning representation thường hiệu quả hơn thay model quá sớm.
- Có một backup ổn định là rất đáng giá trong branch battle.

### Bước tiếp theo

- Sang Phase 4, M1 nên:
  - giữ `word12_binary_c6` làm candidate chính
  - giữ `word12_tfidf_c2_min2` làm backup ổn định
  - thử 1-2 hướng cuối có chủ đích quanh nhóm text-only mạnh nhất
  - chỉ thử hybrid tiếp nếu có giả thuyết feature rất cụ thể

---

## Phase 4 - Tối ưu tiếp quanh nhóm text-only mạnh nhất

### Mục tiêu

- không rẽ sang hybrid nữa
- chỉ tập trung vào text-only quanh nhóm candidate tốt nhất của Phase 3
- kiểm tra xem có nên giữ single model hay chuyển sang text-only ensemble

### Việc đã làm

- viết script:
  - `scripts/run_m1_phase4_text_optimization.py`
- thử hai hướng chính:
  - representation variant quanh single model mạnh nhất
  - probability blend giữa các model text mạnh nhất
- sinh:
  - `reports/battle_m1/phase4_results.csv`
  - `reports/battle_m1/phase4_experiment_summary.md`
  - `data/submissions/sub_m1_v3_phase4_text_ensemble.csv`
- cập nhật tracker và submission log

### Candidate đã thử trong Phase 4

| Run ID | Candidate | Type | CV Macro F1 | Std |
|---|---|---|---:|---:|
| exp_m1_014 | ens_best_backup_50_50 | ensemble | 0.337629 | 0.024355 |
| exp_m1_016 | ens_best_backup_55_45 | ensemble | 0.336599 | 0.030157 |
| exp_m1_015 | ens_best_backup_40_60 | ensemble | 0.333967 | 0.022822 |
| exp_m1_013 | binary_tfidf_c4 | single_model | 0.333087 | 0.041163 |
| exp_m1_012 | binary_count_c6 | single_model | 0.321457 | 0.027738 |

### Quyết định đã chốt

- Winner của Phase 4 là:
  - `exp_m1_014`
  - `ens_best_backup_50_50`
- Cấu hình winner:
  - `50% phase3_best_binary_tfidf_c6`
  - `50% phase3_backup_tfidf_min2_c2`
- Kết quả chính:
  - Phase 3 best: `0.334261`
  - Phase 4 best: `0.337629`
  - Gain: `+0.003368`
- Đây là candidate mới mạnh nhất của branch M1 tính đến hiện tại.

### Vì sao chọn text-only ensemble này

- Đây là candidate có `CV mean` cao nhất trong toàn bộ Phase 4.
- Quan trọng hơn, nó không chỉ tăng mean mà còn giảm `std` xuống `0.024355`, tức ổn định hơn đáng kể so với single best model của Phase 3.
- Blend này tận dụng được hai tính chất bổ sung:
  - `phase3_best_binary_tfidf_c6` có peak score cao hơn
  - `phase3_backup_tfidf_min2_c2` ổn định hơn
- Khi trộn 50/50, hai model bù cho nhau tốt hơn nhiều so với việc tiếp tục chỉ tune một model đơn lẻ.

### Hướng nào bị loại và vì sao

- `binary_count_c6`:
  - xác nhận rằng pure binary count không mạnh bằng hướng `binary + idf`
- `binary_tfidf_c4`:
  - gần tốt nhưng không vượt được best single model của Phase 3
- `ensemble 40/60`:
  - khá ổn định nhưng mean chưa bằng winner
- `ensemble 55/45`:
  - tốt nhưng vẫn thấp hơn 50/50

### Insight quan trọng nhất rút ra từ Phase 4

- Hướng text-only của M1 đã đủ mạnh để bước sang giai đoạn “kết hợp các model text tốt nhất với nhau”, không cần phải kéo metadata vào.
- Blend giữa model mean-strong và model variance-stable là một chiến lược rất hợp với dataset nhỏ.
- Phase 4 cũng cho thấy:
  - representation đơn lẻ tốt nhất vẫn là `binary word presence + OVR Logistic Regression`
  - nhưng candidate tổng thể tốt nhất hiện tại lại là `ensemble` của hai model text-only

### Bài rút ra

- Không phải lúc nào bước tiếp theo sau tuning cũng là đổi feature; đôi khi blend các candidate đã tốt sẵn cho hiệu quả cao hơn.
- Với dataset nhỏ, giảm variance có giá trị thực tế gần như tăng mean.
- Việc giữ lại candidate backup từ Phase 3 là quyết định đúng, vì nó đã trở thành một nửa của winner Phase 4.

### Bước tiếp theo

- Sang phase tiếp theo, M1 nên:
  - giữ `exp_m1_014` làm candidate chính
  - kiểm tra error analysis giữa ensemble winner và single-model winner
  - nếu cần nộp nhiều bản, dùng:
    - `sub_m1_v3_phase4_text_ensemble.csv` làm candidate chính
    - `sub_m1_v2_phase3_best.csv` làm single-model backup

---

## Phase 5 - Error analysis giữa single winner và ensemble winner

### Mục tiêu

- hiểu rõ vì sao `exp_m1_014` đang thắng `exp_m1_002`
- xem ensemble cải thiện ở lớp nào và trả giá ở lớp nào
- xác định các vùng nhầm lẫn cần tập trung nếu còn tối ưu tiếp

### Việc đã làm

- viết script:
  - `scripts/run_m1_phase5_error_analysis.py`
- tạo out-of-fold predictions trên cùng `StratifiedKFold`
- so sánh:
  - single-model reference `exp_m1_002`
  - ensemble winner `exp_m1_014`
- sinh:
  - `reports/battle_m1/phase5_error_analysis.md`
  - `reports/battle_m1/phase5_cv_predictions.csv`
  - `reports/battle_m1/phase5_per_class_metrics.csv`
  - `reports/battle_m1/phase5_confusion_single.csv`
  - `reports/battle_m1/phase5_confusion_ensemble.csv`

### Lưu ý về metric

- Chọn model của branch vẫn dựa trên **mean fold Macro F1**.
- Error analysis dùng **aggregated out-of-fold predictions** để nhìn được từng sample ở chế độ held-out.
- Vì vậy số OOF trong report có thể lệch nhẹ so với score mean-fold đã dùng để chọn winner.

### Kết quả chính

- Single OOF Macro F1: `0.337404`
- Ensemble OOF Macro F1: `0.340033`
- Ensemble sửa đúng thêm: `17` mẫu
- Ensemble làm hỏng: `16` mẫu

### So sánh theo lớp

| Label | Single F1 | Ensemble F1 | Delta |
|---|---:|---:|---:|
| 1 | 0.501901 | 0.526316 | +0.024415 |
| 2 | 0.320000 | 0.316832 | -0.003168 |
| 3 | 0.187500 | 0.184049 | -0.003451 |
| 4 | 0.192771 | 0.202381 | +0.009610 |
| 5 | 0.484848 | 0.470588 | -0.014260 |

### Quyết định đã chốt

- Vẫn giữ `exp_m1_014` là candidate chính của M1.
- Lý do:
  - tốt hơn về tổng thể
  - ổn định hơn qua folds
  - gain thực tế không chỉ nằm ở score mean mà còn đến từ hành vi lỗi “cân bằng” hơn

### Vì sao ensemble vẫn đáng chọn

- Nó cải thiện rõ trên Label 1 và Label 4.
- Nó sửa được slightly more cases than it hurts.
- Quan trọng hơn, Phase 4 winner vốn đã thắng về mean-fold CV và Phase 5 cho thấy chiến thắng đó không phải ngẫu nhiên.
- Blend giữa hai model text-only thật sự tạo ra decision boundary khác hữu ích, nhất là với các case mỏng tín hiệu.

### Trade-off quan trọng nhất

- Ensemble làm giảm F1 của Label 5.
- Điều này khớp với một số case bị “hurt by ensemble”, nơi single model vốn đã đúng và ensemble kéo sang Label 3 hoặc Label 4.
- Vì vậy `exp_m1_002` vẫn nên được giữ như một fallback hợp lý, nhất là nếu Public LB sau này ưu ái behavior của single model hơn.

### Các vùng nhầm lẫn khó nhất hiện tại

- `1 -> 2`
- `2 -> 1`
- `4 -> 5`
- `3 -> 4`
- `3 -> 5`

### Bài rút ra

- Bước từ Phase 4 sang Phase 5 xác nhận rằng ensemble của M1 không chỉ “ăn may score”, mà có pattern cải thiện thật.
- Tuy nhiên branch M1 vẫn chưa giải quyết được bài toán phân biệt tốt các lớp trung gian như Label 3 và Label 4.
- Nếu còn tối ưu tiếp, nên nghĩ theo “cặp lớp hay nhầm” chứ không cần mở thêm nhánh feature lớn.

### Bước tiếp theo

- Nếu chạy phase tiếp:
  - ưu tiên phân tích sâu các case `1/2`, `4/5`, `3/4/5`
  - cân nhắc sinh 2 candidate cuối để nộp:
    - ensemble winner `exp_m1_014`
    - single fallback `exp_m1_002`

---

## Showdown Prep - Final comparison sheet cho M1

### Mục tiêu

- đóng gói toàn bộ tiến trình M1 thành một comparison sheet ngắn gọn nhưng đủ bằng chứng
- giúp sau này đem branch M1 ra đối đầu trực tiếp với M2/M3/M4 mà không phải đọc lại toàn bộ phase log

### Việc đã làm

- tạo script:
  - `scripts/build_m1_final_comparison_sheet.py`
- sinh:
  - `reports/battle_m1/final_comparison_sheet.md`
  - `reports/battle_m1/final_comparison_candidates.csv`

### Quyết định đã chốt cho showdown

- Main candidate:
  - `exp_m1_014`
  - `sub_m1_v3_phase4_text_ensemble.csv`
- Primary backup:
  - `exp_m1_002`
  - `sub_m1_v2_phase3_best.csv`
- Stability reserve:
  - `exp_m1_011`

### Vì sao set up như vậy

- `exp_m1_014` là best overall candidate của M1:
  - mean CV cao nhất
  - variance thấp hơn đáng kể
  - error analysis xác nhận thắng lợi có ý nghĩa
- `exp_m1_002` vẫn cần giữ:
  - dễ giải thích hơn
  - là single-model reference mạnh
  - hữu ích nếu Public LB sau này không favor ensemble
- `exp_m1_011` là reserve quan trọng:
  - không phải candidate chính
  - nhưng giải thích rất tốt vì sao ensemble winner của Phase 4 hoạt động được

### Bài rút ra

- M1 giờ đã ở trạng thái đủ tốt để đi vào “branch showdown”.
- Comparison sheet giúp biến toàn bộ branch từ một chuỗi phase thành một “battle card” rõ ràng, dễ so sánh với các branch khác.

---

## Phase 6 - Final submission strategy cho Kaggle

### Mục tiêu

- chốt playbook nộp bài cuối cho M1
- xác định bản nào nộp trước, bản nào giữ làm backup, bản nào chỉ giữ nội bộ
- tránh việc đổi candidate theo cảm tính khi Public LB xuất hiện

### Việc đã làm

- tổng hợp lại bằng chứng từ:
  - `final_comparison_sheet.md`
  - `phase5_error_analysis.md`
  - `submission_log.csv`
- tạo:
  - `reports/battle_m1/final_submission_strategy.md`
  - `reports/battle_m1/final_submission_queue.csv`
- cập nhật branch note và branch config để strategy này trở thành state chính thức của M1

### Quyết định đã chốt

- Submit first:
  - `sub_m1_v3_phase4_text_ensemble.csv`
- Primary Kaggle backup:
  - `sub_m1_v2_phase3_best.csv`
- Internal reserve:
  - `exp_m1_011`
- Baseline chỉ giữ cho sanity-check:
  - `sub_m1_v1_text_word12_ovr_lr.csv`

### Vì sao nộp ensemble trước

- `exp_m1_014` đang là best overall candidate của M1 trên cả:
  - mean CV
  - CV variance
  - OOF error analysis
- Nếu M1 không nộp candidate này trước, branch sẽ không đo được trần điểm thật sự của hướng đang mạnh nhất.
- Backup single-model nên được dùng như một hedge có chủ đích, không nên chiếm vị trí main candidate ngay từ đầu.

### Vì sao giữ `exp_m1_002` làm backup chính

- Đây là single-model mạnh nhất của M1.
- Nó mang value chiến thuật rõ ràng:
  - dễ giải thích
  - đủ gần với main candidate về điểm
  - phù hợp để test xem leaderboard có disagree với ensemble hay không
- Giữ backup kiểu này giúp M1 có phương án phản ứng nhanh mà không cần quay về baseline yếu hơn.

### Vì sao chưa dùng `exp_m1_011` làm submission mặc định

- `exp_m1_011` rất hữu ích về mặt stability story, nhưng mean score vẫn thấp hơn hai candidate chính.
- Value lớn nhất của nó hiện tại là:
  - làm thành phần của winner Phase 4
  - làm reserve nếu top candidates đều cho tín hiệu LB không tốt
- Nộp reserve quá sớm sẽ làm loãng chiến lược submission mà chưa có đủ bằng chứng lợi ích.

### Decision rule sau khi có LB

- Nếu backup chỉ hơn main rất ít, trong khoảng `<= 0.002`, vẫn giữ main candidate.
- Nếu backup hơn main `> 0.002`, promote backup thành official M1 candidate.
- Không đổi candidate chính chỉ vì chênh lệch rất nhỏ, vì M1 đang có evidence tổng thể tốt hơn ở ensemble winner.

### Bài rút ra

- Giai đoạn cuối không chỉ là “có model nào mạnh nhất”, mà là “ra quyết định nộp bài như thế nào để không tự phá lợi thế của branch”.
- M1 hiện đã có một submission strategy đủ rõ để đem đi Kaggle battle mà không bị dao động bởi các tín hiệu ngắn hạn.

---

## Phase 7 - ModernBERT upgrade sau khi Kaggle feedback quá thấp

### Mục tiêu

- nâng M1 lên một họ model text hiện đại hơn thay vì tiếp tục chỉ xoay quanh TF-IDF
- tìm xem semantic encoder có bổ sung gì cho sparse ensemble hiện tại hay không
- tạo submission mới đủ mạnh để thay luôn main candidate cũ nếu thắng rõ ràng

### Việc đã làm

- cập nhật dependency để repo chạy được `transformers` và `sentence-transformers`
- thêm helper dựng structured text cho encoder
- viết script:
  - `scripts/run_m1_phase7_modernbert_upgrade.py`
- benchmark trên cùng shared CV:
  - `ModernBERT` title-only encoder
  - `ModernBERT` structured encoder (`title + venue + year + authors`)
  - blend giữa phase-4 lexical ensemble và structured `ModernBERT`
- sinh:
  - `reports/battle_m1/phase7_transformer_results.csv`
  - `reports/battle_m1/phase7_transformer_summary.md`
  - `data/submissions/sub_m1_v4_phase7_modernbert_blend.csv`
- cập nhật tracker và submission log

### Kết quả chính

- Best standalone `ModernBERT` encoder:
  - `exp_m1_018`
  - CV Macro F1: `0.343358`
  - CV std: `0.060626`
- Best overall candidate:
  - `exp_m1_019`
  - `phase4_modernbert_structured_c2_0_w0_56`
  - CV Macro F1: `0.355191`
  - CV std: `0.032478`
- Improvement so với phase-4 winner:
  - `+0.017562`

### Quyết định đã chốt

- Main candidate mới của M1 là:
  - `exp_m1_019`
  - `sub_m1_v4_phase7_modernbert_blend.csv`
- Lexical backup mới là:
  - `exp_m1_014`
  - `sub_m1_v3_phase4_text_ensemble.csv`
- Semantic reserve là:
  - `exp_m1_018`

### Vì sao chọn hướng này

- User feedback từ Kaggle cho thấy branch cần một text method hiện đại hơn.
- Trong điều kiện CPU-only, `frozen encoder + linear head` là cách nhanh nhất để lấy transformer signal đáng tin mà vẫn benchmark được công bằng trên 5-fold CV.
- Kết quả mạnh nhất không đến từ việc bỏ sparse model cũ, mà từ việc blend:
  - lexical precision của phase-4 ensemble
  - semantic signal của `ModernBERT`
- Điều này xác nhận giả thuyết quan trọng:
  - sparse text của M1 vốn không tệ
  - vấn đề là branch còn thiếu semantic smoothing cho các case wording khác nhau nhưng cùng chủ đề

### Hướng đã cân nhắc nhưng chưa ưu tiên

- fine-tune transformer end-to-end ngay trên CPU:
  - khả thi nhưng chi phí thời gian cao hơn đáng kể
  - với feedback Kaggle cần phản ứng nhanh, frozen encoder cho tỷ lệ hiệu quả / thời gian tốt hơn
- semantic-only deployment:
  - best standalone encoder vẫn yếu hơn best blend
  - variance cũng cao hơn, nên chưa hợp lý để làm main candidate

### Bài rút ra

- “Hiện đại hơn” không nhất thiết phải là bỏ toàn bộ pipeline cũ; nhiều khi bước tốt nhất là ghép semantic encoder vào một lexical backbone đã chứng minh được giá trị.
- Với dataset nhỏ, hướng transformer đúng nhất thường là hướng bổ sung tín hiệu cho model đang mạnh, không phải fine-tune nặng bằng mọi giá.
- M1 hiện có một phase-7 winner đủ mạnh để thay đổi hẳn submission strategy của branch.
