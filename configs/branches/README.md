# Branch Configs

Thư mục này chứa config riêng cho từng branch battle.

## Mục tiêu

- Giữ cho mỗi branch có cấu hình thử nghiệm riêng mà không phá luật chung của repo.
- Tách được strategy, naming và output path của từng thành viên.
- Dễ tái chạy pipeline của từng branch sau này.

## Quy ước

- Mỗi branch battle có một file YAML riêng.
- Không thay đổi các rule chung như CV hoặc metric nếu cả nhóm chưa thống nhất.
- Config branch chỉ nên ghi:
  - owner
  - branch name
  - strategy hiện tại
  - run id / submission id đầu tiên
  - output path
