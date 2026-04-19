from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler

from ensemble_experiment import (
    LABEL_COL,
    RANDOM_STATE,
    TRAIN_PATH,
    MetadataBuilder,
    clean_text,
    doi_prefix,
    doi_suffix_head,
    make_text_vectorizer,
    parse_authors,
)


OUTPUT_DIR = Path(__file__).resolve().parent / "feature_visualizations"
PLOT_DIR = OUTPUT_DIR / "plots"


def save_plot(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()


def add_2d_projection(
    matrix,
    labels: pd.Series,
    name: str,
    output_path: Path,
) -> pd.DataFrame:
    svd = TruncatedSVD(n_components=2, random_state=RANDOM_STATE)
    coords = svd.fit_transform(matrix)
    plot_df = pd.DataFrame(
        {
            f"{name}_svd_1": coords[:, 0],
            f"{name}_svd_2": coords[:, 1],
            LABEL_COL: labels.astype(str).to_numpy(),
        }
    )

    plt.figure(figsize=(9, 6))
    ax = sns.scatterplot(
        data=plot_df,
        x=f"{name}_svd_1",
        y=f"{name}_svd_2",
        hue=LABEL_COL,
        palette="tab10",
        s=46,
        alpha=0.82,
        edgecolor="white",
        linewidth=0.4,
    )
    ax.set_title(f"{name.replace('_', ' ').title()} 2D Projection After Transform")
    ax.set_xlabel(f"{name} SVD component 1")
    ax.set_ylabel(f"{name} SVD component 2")
    ax.legend(title=LABEL_COL, bbox_to_anchor=(1.02, 1), loc="upper left")
    save_plot(output_path)
    return plot_df


def plot_metadata_boxplots(metadata: pd.DataFrame, labels: pd.Series) -> list[Path]:
    selected = [
        "title_word_count",
        "title_char_count",
        "title_avg_word_length",
        "author_count",
        "author_frequency_mean",
        "author_frequency_max",
        "doi_length",
        "doi_digit_count",
        "doi_slash_count",
        "doi_dot_count",
        "year_normalized",
        "paper_age",
    ]
    selected = [feature for feature in selected if feature in metadata.columns]
    plot_df = metadata[selected].copy()
    plot_df[LABEL_COL] = labels.astype(str).to_numpy()

    paths = []
    for feature in selected:
        path = PLOT_DIR / f"boxplot_{feature}_by_label.png"
        plt.figure(figsize=(9, 5))
        ax = sns.boxplot(data=plot_df, x=LABEL_COL, y=feature, hue=LABEL_COL, palette="tab10")
        ax.set_title(f"{feature} After Transform By Label")
        ax.set_xlabel("Label")
        ax.set_ylabel(feature)
        if ax.legend_ is not None:
            ax.legend_.remove()
        save_plot(path)
        paths.append(path)
    return paths


def plot_top_tfidf_terms_by_label(
    text_matrix,
    vectorizer,
    labels: pd.Series,
    top_k: int = 12,
) -> Path:
    names = vectorizer.get_feature_names_out()
    rows = []
    for label in sorted(labels.unique()):
        mask = (labels == label).to_numpy()
        mean_scores = np.asarray(text_matrix[mask].mean(axis=0)).ravel()
        top_idx = mean_scores.argsort()[-top_k:][::-1]
        for idx in top_idx:
            rows.append(
                {
                    LABEL_COL: str(label),
                    "term": names[idx],
                    "mean_tfidf": mean_scores[idx],
                }
            )

    top_terms = pd.DataFrame(rows)
    top_terms.to_csv(OUTPUT_DIR / "top_tfidf_terms_by_label.csv", index=False)

    path = PLOT_DIR / "top_tfidf_terms_by_label.png"
    grid = sns.catplot(
        data=top_terms,
        kind="bar",
        x="mean_tfidf",
        y="term",
        col=LABEL_COL,
        col_wrap=3,
        sharey=False,
        height=4,
        aspect=1.05,
        color="#4C78A8",
    )
    grid.fig.suptitle("Top TF-IDF Terms After Clean And Transform", y=1.02)
    grid.set_axis_labels("Mean TF-IDF", "Term")
    grid.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(grid.fig)
    return path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    df = pd.read_csv(TRAIN_PATH)
    labels = df[LABEL_COL]

    cleaned = df.copy()
    cleaned["title_clean"] = cleaned["title"].map(clean_text)
    cleaned["venue_clean"] = cleaned["venue"].map(clean_text)
    cleaned["authors_raw"] = cleaned["authors"]
    cleaned["authors_parsed"] = cleaned["authors"].map(parse_authors).map(
        lambda values: " | ".join(values)
    )
    cleaned["authors_is_missing"] = cleaned["authors_parsed"].eq("").astype(int)
    cleaned["doi_clean"] = cleaned["doi"].map(clean_text)
    cleaned["doi_prefix"] = cleaned["doi"].map(doi_prefix)
    cleaned["doi_suffix_head"] = cleaned["doi"].map(doi_suffix_head)
    cleaned["doi_suffix_head_missing"] = cleaned["doi_suffix_head"].eq("").astype(int)
    cleaned[
        [
            "title_clean",
            "venue_clean",
            "authors_raw",
            "authors_parsed",
            "authors_is_missing",
            "doi_clean",
            "doi_prefix",
            "doi_suffix_head",
            "doi_suffix_head_missing",
            LABEL_COL,
        ]
    ].to_csv(
        OUTPUT_DIR / "cleaned_feature_preview.csv",
        index=False,
    )

    metadata_builder = MetadataBuilder(rare_threshold=2)
    metadata = metadata_builder.fit_transform(df)
    metadata[LABEL_COL] = labels.to_numpy()
    metadata.to_csv(OUTPUT_DIR / "transformed_metadata_features.csv", index=False)

    metadata_features = metadata.drop(columns=[LABEL_COL])
    scaler = StandardScaler()
    metadata_scaled = scaler.fit_transform(metadata_features)

    text_vectorizer = make_text_vectorizer()
    text_matrix = text_vectorizer.fit_transform(df["title"].fillna(""))

    text_projection = add_2d_projection(
        text_matrix,
        labels,
        "title_tfidf",
        PLOT_DIR / "title_tfidf_svd_by_label.png",
    )
    text_projection.to_csv(OUTPUT_DIR / "title_tfidf_svd_projection.csv", index=False)

    metadata_projection = add_2d_projection(
        metadata_scaled,
        labels,
        "metadata",
        PLOT_DIR / "metadata_svd_by_label.png",
    )
    metadata_projection.to_csv(OUTPUT_DIR / "metadata_svd_projection.csv", index=False)

    title_svd = TruncatedSVD(n_components=20, random_state=RANDOM_STATE).fit_transform(text_matrix)
    combined_matrix = np.hstack([metadata_scaled, title_svd])
    combined_projection = add_2d_projection(
        combined_matrix,
        labels,
        "combined_features",
        PLOT_DIR / "combined_features_svd_by_label.png",
    )
    combined_projection.to_csv(OUTPUT_DIR / "combined_features_svd_projection.csv", index=False)

    boxplot_paths = plot_metadata_boxplots(metadata_features, labels)
    top_terms_path = plot_top_tfidf_terms_by_label(text_matrix, text_vectorizer, labels)

    plot_paths = [
        PLOT_DIR / "title_tfidf_svd_by_label.png",
        PLOT_DIR / "metadata_svd_by_label.png",
        PLOT_DIR / "combined_features_svd_by_label.png",
        top_terms_path,
        *boxplot_paths,
    ]

    lines = [
        "# Transformed Feature Visualization",
        "",
        "## Goal",
        "",
        "Visualize features after cleaning/transformation and before classifier fitting, colored by `Label`.",
        "",
        "## Transform Steps",
        "",
        "- Cleaned text fields with the same `clean_text` function used in the ensemble pipeline.",
        "- Built fold-style metadata features with `MetadataBuilder` on the full train set for visualization.",
        "- Built title TF-IDF with word 1-2 grams and char 3-5 grams.",
        "- Used TruncatedSVD only for visualization because TF-IDF is high-dimensional.",
        "",
        "## Main Plots",
        "",
        "![Title TF-IDF SVD](plots/title_tfidf_svd_by_label.png)",
        "",
        "![Metadata SVD](plots/metadata_svd_by_label.png)",
        "",
        "![Combined Features SVD](plots/combined_features_svd_by_label.png)",
        "",
        "![Top TF-IDF Terms](plots/top_tfidf_terms_by_label.png)",
        "",
        "## Generated Files",
        "",
        "- `cleaned_feature_preview.csv`: cleaned title, venue, DOI and label.",
        "- `transformed_metadata_features.csv`: metadata features after engineering.",
        "- `title_tfidf_svd_projection.csv`: 2D SVD coordinates from title TF-IDF.",
        "- `metadata_svd_projection.csv`: 2D SVD coordinates from metadata features.",
        "- `combined_features_svd_projection.csv`: 2D SVD coordinates from metadata plus title SVD.",
        "- `top_tfidf_terms_by_label.csv`: strongest mean TF-IDF terms per label.",
        "",
        "## Plot Files",
        "",
        *[f"- `{path.as_posix()}`" for path in plot_paths],
    ]
    (OUTPUT_DIR / "feature_visualization_report.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"Feature visualizations written to: {OUTPUT_DIR}")
    print(f"Report: {OUTPUT_DIR / 'feature_visualization_report.md'}")


if __name__ == "__main__":
    main()
