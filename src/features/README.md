# src.features

Module này chứa phần tiền xử lý và feature engineering.

## File hiện có

- `preprocess.py`: hàm normalize text và parse authors/doi đơn giản.
- `metadata.py`: dựng bảng feature metadata cơ bản.
- `text.py`: helper cho text series và TF-IDF vectorizer.
- `text.py` cũng có helper ghép `title + metadata` thành một text field cho encoder/transformer.

## Cách dùng trong mô hình 4 branch

- Mỗi thành viên có thể chọn dùng một phần hoặc toàn bộ module này.
- Không có ownership cố định; ai cũng có thể mở rộng text hoặc metadata features trên branch riêng.
