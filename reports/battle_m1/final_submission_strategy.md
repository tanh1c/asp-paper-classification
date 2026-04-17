# Final Submission Strategy - M1

## Mục tiêu

- chốt thứ tự nộp bài lên Kaggle cho M1
- tránh đổi candidate theo cảm tính khi Public LB bắt đầu xuất hiện
- giữ một main candidate rõ ràng nhưng vẫn có backup hợp lý

## Branch snapshot trước khi submit

| Role | Run ID | Submission ID | File | CV Macro F1 | Std | OOF Macro F1 | Ghi chú |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| main_candidate | `exp_m1_014` | `sub_m1_003` | `sub_m1_v3_phase4_text_ensemble.csv` | 0.337629 | 0.024355 | 0.340033 | best overall candidate của M1 |
| primary_backup | `exp_m1_002` | `sub_m1_002` | `sub_m1_v2_phase3_best.csv` | 0.334261 | 0.041403 | 0.337404 | best single-model hedge |
| stability_reserve | `exp_m1_011` | - | chưa export riêng | 0.330420 | 0.023573 | - | reserve thiên về độ ổn định |
| baseline_reference | `exp_m1_001` | `sub_m1_001` | `sub_m1_v1_text_word12_ovr_lr.csv` | 0.327027 | 0.032543 | - | chỉ dùng làm reference/sanity check |

## Thứ tự submit khuyến nghị

### Lượt 1

- Nộp trước: `sub_m1_v3_phase4_text_ensemble.csv`
- Lý do:
  - đây là candidate có `CV mean` tốt nhất của M1
  - `std` thấp hơn rõ rệt so với backup single-model
  - error analysis cho thấy ensemble thắng không chỉ vì fold noise

### Lượt 2

- Giữ sẵn để nộp tiếp: `sub_m1_v2_phase3_best.csv`
- Lý do:
  - đây là candidate single-model mạnh nhất và dễ giải thích nhất
  - phù hợp làm hedge nếu Public LB không thích ensemble bias
  - useful để kiểm tra xem leaderboard có disagree với CV story của M1 hay không

### Không ưu tiên nộp ngay

- `exp_m1_011`:
  - giữ làm reserve nội bộ
  - chỉ nên export/submission nếu cả main và backup đều cho LB thất vọng hoặc nhóm còn dư slot và muốn thử một candidate thấp variance
- `sub_m1_v1_text_word12_ovr_lr.csv`:
  - không dùng làm candidate tranh điểm
  - chỉ nộp khi cần sanity-check pipeline hoặc format submission

## Decision rules sau khi có Public LB

### Giữ `exp_m1_014` làm candidate chính nếu

- `sub_m1_v3_phase4_text_ensemble.csv` đang là submission M1 có Public LB cao nhất
- hoặc backup chỉ hơn rất ít, trong khoảng `<= 0.002`

Lý do:

- main candidate có bằng chứng tổng thể tốt hơn:
  - CV mean cao hơn
  - OOF tốt hơn
  - variance thấp hơn
- nếu LB chênh rất nhỏ, nên ưu tiên candidate có story ổn định hơn thay vì đổi vì nhiễu ngắn hạn

### Chuyển sang `exp_m1_002` làm official M1 candidate nếu

- `sub_m1_v2_phase3_best.csv` hơn main candidate `> 0.002` trên Public LB
- hoặc main candidate có hành vi rất bất thường so với CV story, trong khi backup bám sát kỳ vọng hơn

Lý do:

- khoảng chênh kiểu này đủ đáng kể để cân nhắc rằng leaderboard thích decision boundary của single-model hơn
- backup vẫn đủ mạnh để đại diện cho M1 mà không làm yếu branch quá nhiều

### Chưa nên đụng tới reserve nếu

- main và backup đang chênh không lớn
- nhóm chưa có dấu hiệu rằng leaderboard ưu ái low-variance candidate hơn

`exp_m1_011` chủ yếu dùng để giải thích thiết kế của ensemble winner và làm reserve chiến thuật, không phải default Kaggle choice.

## Tại sao M1 vẫn nộp ensemble trước

- `exp_m1_014` là candidate tốt nhất của M1 trên cả ba lớp bằng chứng:
  - mean CV
  - CV stability
  - OOF error analysis
- Nếu không nộp ensemble trước, M1 sẽ không đo được đúng “ceiling” hiện tại của branch.
- Backup single-model nên được dùng như một phép sanity-check của leaderboard, không nên đảo vai trò với main candidate ngay từ đầu.

## Playbook thao tác sau mỗi lần submit

1. Ghi `public_lb` vào `experiments/submission_log.csv`.
2. Cập nhật `notes` theo format ngắn:
   - `phase6 main candidate first wave`
   - `phase6 backup hedge against ensemble`
3. Nếu backup vượt main rõ rệt, cập nhật lại candidate order trong:
   - `reports/battle_m1/final_comparison_sheet.md`
   - `reports/battle_m1/final_submission_strategy.md`
4. Không đổi official candidate của M1 chỉ vì chênh rất nhỏ.

## Recommendation cuối cùng

- Submit first:
  - `sub_m1_v3_phase4_text_ensemble.csv`
- Hold as Kaggle backup:
  - `sub_m1_v2_phase3_best.csv`
- Keep as internal reserve:
  - `exp_m1_011`
- Keep only for sanity/reference:
  - `sub_m1_v1_text_word12_ovr_lr.csv`
