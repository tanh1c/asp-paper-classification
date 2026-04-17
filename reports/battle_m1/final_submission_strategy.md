# Final Submission Strategy - M1

## Mục tiêu

- chốt thứ tự nộp Kaggle mới cho M1 sau khi branch đã có winner thuộc họ `ModernBERT`
- tránh quay lại candidate cũ theo cảm tính
- giữ rõ vai trò giữa main blend, lexical backup và semantic reserve

## Branch snapshot trước khi submit

| Role | Run ID | Submission ID | File | CV Macro F1 | Std | Ghi chú |
| --- | --- | --- | --- | ---: | ---: | --- |
| main_candidate | `exp_m1_019` | `sub_m1_004` | `sub_m1_v4_phase7_modernbert_blend.csv` | 0.355191 | 0.032478 | winner mới của M1 |
| primary_backup | `exp_m1_014` | `sub_m1_003` | `sub_m1_v3_phase4_text_ensemble.csv` | 0.337629 | 0.024355 | lexical fallback đã battle-tested |
| semantic_reserve | `exp_m1_018` | - | chưa export riêng | 0.343358 | 0.060626 | best standalone ModernBERT encoder |
| legacy_reference | `exp_m1_002` | `sub_m1_002` | `sub_m1_v2_phase3_best.csv` | 0.334261 | 0.041403 | reference single-model cũ |

## Thứ tự submit khuyến nghị

### Lượt 1

- Nộp trước: `sub_m1_v4_phase7_modernbert_blend.csv`
- Lý do:
  - đây là candidate có `CV mean` cao nhất toàn branch M1 hiện tại
  - improvement so với winner cũ đủ lớn (`+0.017562`)
  - semantic encoder đã được chứng minh là có value thực chứ không chỉ là “đổi model cho hiện đại”

### Lượt 2

- Giữ sẵn để nộp tiếp: `sub_m1_v3_phase4_text_ensemble.csv`
- Lý do:
  - đây là backup variance thấp hơn và đã được error analysis xác nhận
  - nếu leaderboard không thích blend lexical + semantic, đây là fallback đáng tin nhất
  - phase-7 winner thực chất cũng đang xây trên nền lexical ensemble này, nên backup rất tự nhiên

### Chưa ưu tiên nộp ngay

- `exp_m1_018`:
  - giữ làm semantic reserve
  - chỉ nên export/submission nếu main và lexical backup đều underperform hoặc nhóm còn dư slot để test pure semantic behavior
- `sub_m1_v2_phase3_best.csv`:
  - giữ làm legacy reference
  - useful nếu cần sanity-check một single-model dễ giải thích hơn, nhưng không còn là default backup nữa

## Decision rules sau khi có Public LB

### Giữ `exp_m1_019` làm candidate chính nếu

- `sub_m1_v4_phase7_modernbert_blend.csv` đang là submission M1 có Public LB cao nhất
- hoặc lexical backup chỉ hơn rất ít, trong khoảng `<= 0.002`

Lý do:

- main candidate có bằng chứng tổng thể tốt nhất của branch sau phase transformer upgrade
- nếu chênh lệch LB nhỏ, nên ưu tiên candidate có trần CV cao hơn thay vì quay lại fallback quá sớm

### Chuyển sang `exp_m1_014` làm official M1 candidate nếu

- `sub_m1_v3_phase4_text_ensemble.csv` hơn main candidate `> 0.002` trên Public LB
- hoặc main candidate có hành vi bất thường, còn lexical backup bám sát kỳ vọng hơn

Lý do:

- phase-4 backup là candidate đã được kiểm chứng kỹ nhất trên hold-out nội bộ
- nếu leaderboard reject semantic blend, lexical fallback là nước đi an toàn nhất

### Chỉ materialize `exp_m1_018` nếu

- cả main candidate và lexical backup đều cho tín hiệu LB không tốt
- hoặc nhóm còn slot đủ để test semantic-only candidate như một hedge cuối

`exp_m1_018` hiện là reserve chiến thuật, không phải default Kaggle choice.

## Tại sao M1 nộp ModernBERT blend trước

- `exp_m1_019` là candidate mạnh nhất của M1 theo shared CV.
- Nó sửa đúng một vấn đề thật của branch: sparse text cũ thiếu semantic signal.
- Nếu không nộp candidate này trước, M1 sẽ không đo đúng trần điểm hiện tại sau phase transformer upgrade.

## Playbook thao tác sau mỗi lần submit

1. Ghi `public_lb` vào `experiments/submission_log.csv`.
2. Cập nhật `notes` theo format ngắn:
   - `phase7 modernbert main first wave`
   - `phase7 lexical fallback after blend`
3. Nếu lexical backup vượt main rõ rệt, cập nhật lại candidate order trong:
   - `reports/battle_m1/final_comparison_sheet.md`
   - `reports/battle_m1/final_submission_strategy.md`
4. Chỉ export semantic reserve khi top two thật sự không ổn.

## Recommendation cuối cùng

- Submit first:
  - `sub_m1_v4_phase7_modernbert_blend.csv`
- Hold as Kaggle backup:
  - `sub_m1_v3_phase4_text_ensemble.csv`
- Keep as semantic reserve:
  - `exp_m1_018`
- Keep as legacy reference:
  - `sub_m1_v2_phase3_best.csv`
