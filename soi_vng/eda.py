from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys

parrent_dir = Path(__file__).resolve().parent.parent
print(parrent_dir)
sys.path.append(str(parrent_dir))
DATA_PATH = parrent_dir / Path("dataset_stage1") / "Stage_1_publcitrain.csv"
OUTPUT_DIR = Path("eda_outputs")
PLOT_DIR = OUTPUT_DIR / "plots"
LABEL_COL = "Label"
ID_COL = "id"


def table_text(obj) -> str:
    if isinstance(obj, pd.Series):
        return "```\n" + obj.to_string() + "\n```"
    return "```\n" + obj.to_string() + "\n```"


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create simple numeric features so text/category columns can be analyzed."""
    features = pd.DataFrame(index=df.index)

    features["year"] = df["year"]
    features["title_char_count"] = df["title"].fillna("").str.len()
    features["title_word_count"] = df["title"].fillna("").str.split().str.len()
    features["author_count"] = (
        df["authors"]
        .fillna("")
        .apply(lambda value: 0 if value.strip() == "" else len(value.split(",")))
    )
    features["has_authors"] = df["authors"].notna().astype(int)
    features["doi_char_count"] = df["doi"].fillna("").str.len()
    features["has_doi"] = df["doi"].notna().astype(int)

    venue_dummies = pd.get_dummies(df["venue"], prefix="venue", dtype=int)
    features = pd.concat([features, venue_dummies], axis=1)
    features[LABEL_COL] = df[LABEL_COL]
    return features


def save_value_counts(df: pd.DataFrame, output_dir: Path) -> None:
    for col in df.columns:
        counts = (
            df[col]
            .value_counts(dropna=False)
            .rename_axis(col)
            .reset_index(name="count")
        )
        counts["percent"] = counts["count"] / len(df) * 100
        safe_col = col.replace(" ", "_").replace("/", "_")
        counts.to_csv(output_dir / f"value_counts_{safe_col}.csv", index=False)


def save_current_plot(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()


def plot_bar(data: pd.DataFrame, x: str, y: str, title: str, path: Path, hue: str | None = None) -> None:
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(data=data, x=x, y=y, hue=hue)
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=45)
    save_current_plot(path)


def create_plots(
    df: pd.DataFrame,
    overview: pd.DataFrame,
    engineered: pd.DataFrame,
    label_counts: pd.DataFrame,
    corr_with_label: pd.DataFrame,
) -> list[Path]:
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    plot_paths = []

    label_plot = PLOT_DIR / "01_label_distribution.png"
    plot_bar(label_counts, LABEL_COL, "count", "Label distribution", label_plot)
    plot_paths.append(label_plot)

    missing = (
        overview["missing"]
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"index": "feature", "missing": "count"})
    )
    missing_plot = PLOT_DIR / "02_missing_values_by_feature.png"
    plot_bar(missing, "feature", "count", "Missing values by feature", missing_plot)
    plot_paths.append(missing_plot)

    unique = (
        overview["unique"]
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"index": "feature", "unique": "count"})
    )
    unique_plot = PLOT_DIR / "03_unique_values_by_feature.png"
    plot_bar(unique, "feature", "count", "Unique values by feature", unique_plot)
    plot_paths.append(unique_plot)

    venue_counts = df["venue"].value_counts().rename_axis("venue").reset_index(name="count")
    venue_plot = PLOT_DIR / "04_venue_distribution.png"
    plot_bar(venue_counts, "venue", "count", "Venue distribution", venue_plot)
    plot_paths.append(venue_plot)

    year_counts = df["year"].value_counts().sort_index().rename_axis("year").reset_index(name="count")
    year_plot = PLOT_DIR / "05_year_distribution.png"
    plot_bar(year_counts, "year", "count", "Year distribution", year_plot)
    plot_paths.append(year_plot)

    venue_label = pd.crosstab(df["venue"], df[LABEL_COL])
    venue_label_plot = PLOT_DIR / "06_label_by_venue_stacked_bar.png"
    ax = venue_label.plot(kind="bar", stacked=True, figsize=(10, 5))
    ax.set_title("Label by venue")
    ax.set_xlabel("venue")
    ax.set_ylabel("count")
    ax.tick_params(axis="x", rotation=0)
    save_current_plot(venue_label_plot)
    plot_paths.append(venue_label_plot)

    year_label = pd.crosstab(df["year"], df[LABEL_COL])
    year_label_plot = PLOT_DIR / "07_label_by_year_heatmap.png"
    plt.figure(figsize=(11, 6))
    ax = sns.heatmap(year_label, annot=True, fmt="d", cmap="Blues")
    ax.set_title("Label count by year")
    ax.set_xlabel("Label")
    ax.set_ylabel("year")
    save_current_plot(year_label_plot)
    plot_paths.append(year_label_plot)

    corr_plot_data = corr_with_label.dropna().copy()
    corr_plot_data["abs_corr"] = corr_plot_data["corr_with_label"].abs()
    corr_plot_data = corr_plot_data.sort_values("abs_corr", ascending=True)
    corr_plot = PLOT_DIR / "08_feature_corr_with_label.png"
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(data=corr_plot_data, x="corr_with_label", y="feature")
    ax.axvline(0, color="black", linewidth=1)
    ax.set_title("Feature correlation with Label")
    save_current_plot(corr_plot)
    plot_paths.append(corr_plot)

    corr_matrix_plot = PLOT_DIR / "09_engineered_feature_correlation_heatmap.png"
    plt.figure(figsize=(12, 9))
    ax = sns.heatmap(engineered.corr(numeric_only=True), annot=True, fmt=".2f", cmap="vlag", center=0)
    ax.set_title("Engineered feature correlation heatmap")
    save_current_plot(corr_matrix_plot)
    plot_paths.append(corr_matrix_plot)

    cov_matrix_plot = PLOT_DIR / "10_engineered_feature_covariance_heatmap.png"
    plt.figure(figsize=(12, 9))
    ax = sns.heatmap(engineered.drop(columns=[LABEL_COL]).cov(), annot=True, fmt=".2f", cmap="YlGnBu")
    ax.set_title("Engineered feature covariance heatmap")
    save_current_plot(cov_matrix_plot)
    plot_paths.append(cov_matrix_plot)

    std_data = (
        engineered.drop(columns=[LABEL_COL])
        .std()
        .sort_values(ascending=True)
        .rename("std")
        .reset_index()
        .rename(columns={"index": "feature"})
    )
    std_plot = PLOT_DIR / "11_engineered_feature_std.png"
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(data=std_data, x="std", y="feature")
    ax.set_title("Standard deviation of engineered features")
    save_current_plot(std_plot)
    plot_paths.append(std_plot)

    box_features = [
        "year",
        "title_char_count",
        "title_word_count",
        "author_count",
        "doi_char_count",
    ]
    for number, feature in enumerate(box_features, start=12):
        box_plot = PLOT_DIR / f"{number:02d}_{feature}_by_label_boxplot.png"
        plt.figure(figsize=(10, 5))
        ax = sns.boxplot(data=engineered, x=LABEL_COL, y=feature)
        ax.set_title(f"{feature} by Label")
        save_current_plot(box_plot)
        plot_paths.append(box_plot)

    return plot_paths


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    feature_cols = [col for col in df.columns if col not in [LABEL_COL, ID_COL]]
    numeric_original = df.select_dtypes(include="number").columns.drop(
        [LABEL_COL, ID_COL], errors="ignore"
    )
    engineered = add_engineered_features(df)
    numeric_for_relation = engineered.drop(columns=[LABEL_COL])

    overview = pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "count_non_null": df.count(),
            "missing": df.isna().sum(),
            "missing_percent": df.isna().mean() * 100,
            "unique": df.nunique(dropna=True),
        }
    )
    overview.to_csv(OUTPUT_DIR / "feature_overview.csv")

    label_counts = (
        df[LABEL_COL]
        .value_counts()
        .sort_index()
        .rename_axis(LABEL_COL)
        .reset_index(name="count")
    )
    label_counts["percent"] = label_counts["count"] / len(df) * 100
    label_counts.to_csv(OUTPUT_DIR / "label_distribution.csv", index=False)

    save_value_counts(df[feature_cols + [LABEL_COL]], OUTPUT_DIR)

    if len(numeric_original) > 0:
        df[numeric_original].std().rename("std").to_csv(OUTPUT_DIR / "std_original_numeric.csv")
        df[numeric_original].cov().to_csv(OUTPUT_DIR / "cov_original_numeric.csv")

    numeric_for_relation.std().rename("std").to_csv(OUTPUT_DIR / "std_engineered_features.csv")
    numeric_for_relation.cov().to_csv(OUTPUT_DIR / "cov_engineered_features.csv")

    corr_with_label = (
        engineered.corr(numeric_only=True)[LABEL_COL]
        .drop(LABEL_COL)
        .sort_values(key=lambda values: values.abs(), ascending=False)
        .rename("corr_with_label")
        .reset_index()
        .rename(columns={"index": "feature"})
    )
    corr_with_label.to_csv(OUTPUT_DIR / "feature_corr_with_label.csv", index=False)

    by_venue = pd.crosstab(df["venue"], df[LABEL_COL], margins=True)
    by_venue.to_csv(OUTPUT_DIR / "label_by_venue_count.csv")
    pd.crosstab(df["venue"], df[LABEL_COL], normalize="index").to_csv(
        OUTPUT_DIR / "label_by_venue_percent.csv"
    )

    by_year = pd.crosstab(df["year"], df[LABEL_COL], margins=True)
    by_year.to_csv(OUTPUT_DIR / "label_by_year_count.csv")
    pd.crosstab(df["year"], df[LABEL_COL], normalize="index").to_csv(
        OUTPUT_DIR / "label_by_year_percent.csv"
    )

    numeric_by_label = (
        engineered
        .groupby(LABEL_COL)[numeric_for_relation.columns]
        .agg(["count", "mean", "std", "min", "max"])
    )
    numeric_by_label.to_csv(OUTPUT_DIR / "numeric_features_by_label.csv")

    plot_paths = create_plots(df, overview, engineered, label_counts, corr_with_label)

    top_summary = [
        "# EDA Report",
        "",
        f"- Dataset: `{DATA_PATH}`",
        f"- Shape: {df.shape[0]} rows x {df.shape[1]} columns",
        f"- Features used, excluding `{LABEL_COL}` and `{ID_COL}`: {', '.join(feature_cols)}",
        f"- Duplicated rows: {df.duplicated().sum()}",
        "",
        "## Label distribution",
        "",
        "![Label distribution](plots/01_label_distribution.png)",
        "",
        table_text(label_counts),
        "",
        "## Feature overview",
        "",
        "![Missing values by feature](plots/02_missing_values_by_feature.png)",
        "",
        "![Unique values by feature](plots/03_unique_values_by_feature.png)",
        "",
        table_text(overview),
        "",
        "## Original numeric std",
        "",
        (
            table_text(df[numeric_original].std().rename("std"))
            if len(numeric_original) > 0
            else "No original numeric features besides Label/id."
        ),
        "",
        "## Correlation with Label",
        "",
        "![Feature correlation with Label](plots/08_feature_corr_with_label.png)",
        "",
        table_text(corr_with_label),
        "",
        "## Label by venue",
        "",
        "![Label by venue](plots/06_label_by_venue_stacked_bar.png)",
        "",
        table_text(by_venue),
        "",
        "## Label by year",
        "",
        "![Label by year](plots/07_label_by_year_heatmap.png)",
        "",
        table_text(by_year),
        "",
        "## Plot files",
        "",
        *[f"- `{path.as_posix()}`" for path in plot_paths],
        "",
        "## Output files",
        "",
        "- `feature_overview.csv`: dtype, non-null count, missing, unique values",
        "- `label_distribution.csv`: so luong tung Label",
        "- `std_original_numeric.csv`, `cov_original_numeric.csv`: std/cov cua feature numeric goc",
        "- `std_engineered_features.csv`, `cov_engineered_features.csv`: std/cov sau khi tao feature tu text/category",
        "- `feature_corr_with_label.csv`: tuong quan tung feature voi Label",
        "- `label_by_venue_count.csv`, `label_by_year_count.csv`: quan he venue/year voi Label",
        "- `numeric_features_by_label.csv`: mean/std/min/max cua feature numeric theo tung Label",
    ]

    report_path = OUTPUT_DIR / "eda_report.md"
    report_path.write_text("\n".join(top_summary), encoding="utf-8")

    print(f"EDA done. Report: {report_path}")
    print("\nLabel distribution:")
    print(label_counts.to_string(index=False))
    print("\nTop correlations with Label:")
    print(corr_with_label.head(10).to_string(index=False))
    print(f"\nPlots are in: {PLOT_DIR.resolve()}")
    print(f"\nAll output files are in: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
