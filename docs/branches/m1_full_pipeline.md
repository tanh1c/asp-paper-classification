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

- Quick EDA report: `reports/battle_m1/quick_eda.md`
- Baseline summary: `reports/battle_m1/phase2_baseline_summary.md`
- Submission đầu tiên: `data/submissions/sub_m1_v1_text_word12_ovr_lr.csv`

## Checklist Phase 1

- [x] branch battle riêng đã được tạo
- [x] branch note đã được tạo
- [x] branch config đã được tạo
- [x] run id và submission id đầu tiên đã được reserve
- [x] baseline hướng text-first đã được chốt để vào Phase 2
