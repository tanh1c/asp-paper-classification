from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.paths import resolve_project_path


def append_experiment_row(row: dict, tracker_path: str | Path = "experiments/experiment_tracker.csv") -> None:
    """Append one experiment row while keeping the CSV header stable."""
    full_path = resolve_project_path(tracker_path)
    frame = pd.read_csv(full_path)
    updated = pd.concat([frame, pd.DataFrame([row])], ignore_index=True)
    updated.to_csv(full_path, index=False)


def upsert_csv_row(
    row: dict,
    key_field: str,
    tracker_path: str | Path,
) -> None:
    """Insert or replace one CSV row keyed by a stable identifier."""
    full_path = resolve_project_path(tracker_path)
    frame = pd.read_csv(full_path)

    if key_field not in row:
        raise KeyError(f"Missing key field '{key_field}' in row data.")

    row_frame = pd.DataFrame([row])

    if key_field in frame.columns:
        frame = frame[frame[key_field] != row[key_field]]

    ordered_columns = list(frame.columns)
    for column in row_frame.columns:
        if column not in ordered_columns:
            ordered_columns.append(column)

    updated = pd.concat([frame, row_frame], ignore_index=True)
    updated = updated.reindex(columns=ordered_columns)
    updated.to_csv(full_path, index=False)
