from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from src.features.preprocess import normalize_text_series


def build_text_series(
    frame: pd.DataFrame,
    text_column: str = "title",
    normalize: bool = True,
) -> pd.Series:
    """Return a cleaned text series for modeling."""
    raw_series = frame[text_column].fillna("").astype(str)
    if not normalize:
        return raw_series
    return normalize_text_series(raw_series).fillna("")


def build_structured_text_series(
    frame: pd.DataFrame,
    text_column: str = "title",
    include_columns: tuple[str, ...] = ("venue", "year", "authors"),
    missing_token: str = "unknown",
    normalize_columns: bool = True,
) -> pd.Series:
    """Build one structured text field that concatenates title and lightweight metadata."""
    title_series = build_text_series(frame, text_column=text_column, normalize=normalize_columns)
    structured = "title: " + title_series

    for column in include_columns:
        if column not in frame.columns:
            continue

        if column == "year":
            value_series = frame[column].fillna("").astype(str)
            value_series = value_series.where(value_series != "", missing_token)
        else:
            value_series = frame[column].fillna(missing_token).astype(str)
            if normalize_columns:
                value_series = normalize_text_series(value_series).fillna(missing_token)
            value_series = value_series.where(value_series != "", missing_token)

        structured = structured + f" [SEP] {column}: " + value_series

    return structured


def build_tfidf_vectorizer(
    analyzer: str = "word",
    ngram_range: tuple[int, int] = (1, 2),
    min_df: int | float = 1,
    max_df: int | float = 1.0,
    sublinear_tf: bool = True,
    extra_params: dict[str, Any] | None = None,
) -> TfidfVectorizer:
    """Create a TF-IDF vectorizer with sensible defaults for small text datasets."""
    params: dict[str, Any] = {
        "analyzer": analyzer,
        "ngram_range": ngram_range,
        "min_df": min_df,
        "max_df": max_df,
        "sublinear_tf": sublinear_tf,
    }
    if extra_params:
        params.update(extra_params)

    return TfidfVectorizer(**params)
