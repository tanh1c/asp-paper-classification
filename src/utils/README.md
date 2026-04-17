# src.utils

Module này chứa helper nhỏ nhưng dùng xuyên suốt project.

## File hiện có

- `paths.py`: đọc config YAML và resolve đường dẫn theo root repo.
- `logging_utils.py`: append hoặc upsert run vào experiment tracker.

## Lưu ý

- Những helper chung, ngắn và ít phụ thuộc nên đặt ở đây.
- Tránh để utility biến thành nơi chứa logic feature/model khó kiểm soát.
