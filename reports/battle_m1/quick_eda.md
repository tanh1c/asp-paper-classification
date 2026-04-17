# Quick EDA - M1 Branch

## Dataset size

- Train rows: 510
- Test rows: 86
- Train columns: title, venue, year, authors, doi, Label, id
- Test columns: title, venue, year, authors, doi, id

## Data quality checks

- Missing `authors`: 52
- Duplicate `title` in train: 2
- Duplicate `doi` in train: 18

## Label distribution

- Label 1: 130
- Label 2: 103
- Label 3: 85
- Label 4: 89
- Label 5: 103

## Venue distribution

- iclp: 336
- kr: 174

## Branch takeaway

- Dữ liệu còn nhỏ nên baseline text có thể là hướng mở đầu tốt nhất.
- `authors` bị thiếu nhưng không quá lớn; có thể khai thác ở phase sau nếu cần.
- `title` nhiều khả năng là nguồn tín hiệu chính của phase baseline.
