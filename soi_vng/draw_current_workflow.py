from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


OUTPUT_DIR = Path(__file__).resolve().parent / "workflow_diagrams"


def draw_box(ax, xy, text, width=2.6, height=0.72, color="#EAF2F8", edge="#2E5E7E"):
    x, y = xy
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        linewidth=1.2,
        edgecolor=edge,
        facecolor=color,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=9, wrap=True)


def draw_arrow(ax, start, end, color="#444444"):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=11,
        linewidth=1.1,
        color=color,
        shrinkA=18,
        shrinkB=18,
    )
    ax.add_patch(arrow)


def save_figure(fig, name: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def draw_architecture() -> Path:
    fig, ax = plt.subplots(figsize=(17, 10))
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 10)
    ax.axis("off")

    boxes = {
        "raw": ((1.2, 8.8), "Raw train CSV", "#FDEDEC"),
        "cv": ((3.6, 8.8), "Stratified\nK-Fold", "#FDEDEC"),
        "train": ((6.0, 9.35), "Train fold", "#FDEDEC"),
        "valid": ((6.0, 8.25), "Validation fold", "#FDEDEC"),
        "clean_train": ((8.3, 9.35), "Clean title", "#EAF2F8"),
        "clean_valid": ((8.3, 8.25), "Clean title", "#EAF2F8"),
        "tfidf_train": ((10.8, 9.35), "Word TF-IDF\n+ Char TF-IDF", "#EAF2F8"),
        "tfidf_valid": ((10.8, 8.25), "Transform TF-IDF", "#EAF2F8"),
        "logistic": ((13.7, 9.35), "Logistic\nElasticNet", "#E8F8F5"),
        "svc": ((13.7, 8.45), "Calibrated\nLinearSVC", "#E8F8F5"),
        "chi2": ((13.7, 7.55), "AdditiveChi2\n+ LinearSVC", "#E8F8F5"),
        "meta": ((8.3, 6.5), "MetadataBuilder\nvenue/year/doi", "#FEF9E7"),
        "svd": ((10.8, 6.5), "Title TF-IDF\nTruncatedSVD", "#FEF9E7"),
        "boost": ((13.7, 6.5), "Boosting\nLightGBM or HGB", "#E8F8F5"),
        "soft": ((13.7, 4.8), "Fixed\nSoft Voting", "#F4ECF7"),
        "tuned": ((13.7, 3.7), "OOF-Tuned\nSoft Voting", "#F4ECF7"),
        "out": ((13.7, 2.25), "Scores, OOF,\nConfusion Matrix", "#FADBD8"),
        "sub": ((13.7, 1.15), "submission_hieu_<n>.csv", "#FADBD8"),
    }

    for xy, text, color in boxes.values():
        draw_box(ax, xy, text, color=color)

    arrows = [
        ("raw", "cv"),
        ("cv", "train"),
        ("cv", "valid"),
        ("train", "clean_train"),
        ("valid", "clean_valid"),
        ("clean_train", "tfidf_train"),
        ("clean_valid", "tfidf_valid"),
        ("tfidf_train", "logistic"),
        ("tfidf_valid", "logistic"),
        ("tfidf_train", "svc"),
        ("tfidf_valid", "svc"),
        ("tfidf_train", "chi2"),
        ("tfidf_valid", "chi2"),
        ("train", "meta"),
        ("valid", "meta"),
        ("tfidf_train", "svd"),
        ("tfidf_valid", "svd"),
        ("meta", "boost"),
        ("svd", "boost"),
        ("logistic", "soft"),
        ("svc", "soft"),
        ("chi2", "soft"),
        ("boost", "soft"),
        ("logistic", "tuned"),
        ("svc", "tuned"),
        ("chi2", "tuned"),
        ("boost", "tuned"),
        ("soft", "out"),
        ("tuned", "out"),
        ("out", "sub"),
    ]
    for start, end in arrows:
        draw_arrow(ax, boxes[start][0], boxes[end][0])

    ax.text(8.5, 9.95, "Current Ensemble Architecture", ha="center", fontsize=16, weight="bold")
    return save_figure(fig, "current_architecture.png")


def draw_feature_flow() -> Path:
    fig, ax = plt.subplots(figsize=(17, 10))
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 10)
    ax.axis("off")

    boxes = {
        "title": ((1.2, 8.8), "title", "#FDEDEC"),
        "clean": ((3.4, 8.8), "clean_text", "#EAF2F8"),
        "word": ((5.8, 9.25), "Word TF-IDF\n1-2 grams\nstopwords removed", "#EAF2F8"),
        "char": ((5.8, 8.35), "Char TF-IDF\n3-5 grams", "#EAF2F8"),
        "tfidf": ((8.3, 8.8), "Full sparse\nTitle TF-IDF", "#EAF2F8"),
        "text_models": ((11.2, 8.8), "Logistic / SVC /\nChi2-SVC", "#E8F8F5"),
        "svd": ((11.2, 7.55), "TruncatedSVD\nfor boosting", "#FEF9E7"),
        "venue": ((1.2, 6.65), "venue", "#FDEDEC"),
        "year": ((1.2, 4.45), "year", "#FDEDEC"),
        "doi": ((1.2, 3.35), "doi", "#FDEDEC"),
        "venue_feat": ((4.2, 6.65), "clean + rare\n+ one-hot", "#FEF9E7"),
        "year_feat": ((4.2, 4.45), "normalized year\npaper_age\nmissing flag", "#FEF9E7"),
        "doi_feat": ((4.2, 3.35), "prefix + suffix_head\ncounts + missing\nrare + one-hot", "#FEF9E7"),
        "metadata": ((7.6, 4.95), "Metadata matrix\n74 columns", "#FEF9E7"),
        "scale": ((10.4, 4.95), "StandardScaler", "#FEF9E7"),
        "concat": ((13.0, 6.25), "Concat metadata\n+ title SVD", "#FEF9E7"),
        "boost": ((15.3, 6.25), "Boosting model", "#E8F8F5"),
        "vote": ((15.3, 8.1), "Soft voting", "#F4ECF7"),
    }

    for xy, text, color in boxes.values():
        draw_box(ax, xy, text, color=color)

    arrows = [
        ("title", "clean"),
        ("clean", "word"),
        ("clean", "char"),
        ("word", "tfidf"),
        ("char", "tfidf"),
        ("tfidf", "text_models"),
        ("tfidf", "svd"),
        ("venue", "venue_feat"),
        ("year", "year_feat"),
        ("doi", "doi_feat"),
        ("venue_feat", "metadata"),
        ("year_feat", "metadata"),
        ("doi_feat", "metadata"),
        ("metadata", "scale"),
        ("scale", "concat"),
        ("svd", "concat"),
        ("concat", "boost"),
        ("text_models", "vote"),
        ("boost", "vote"),
    ]
    for start, end in arrows:
        draw_arrow(ax, boxes[start][0], boxes[end][0])

    ax.text(8.5, 9.95, "Current Feature Flow", ha="center", fontsize=16, weight="bold")
    return save_figure(fig, "feature_flow.png")


def main() -> None:
    paths = [draw_architecture(), draw_feature_flow()]
    report = [
        "# Rendered Workflow Diagrams",
        "",
        "These PNG diagrams mirror the current Mermaid workflow in `current_workflow.md`.",
        "",
        "## Current Architecture",
        "",
        "![Current Architecture](current_architecture.png)",
        "",
        "## Feature Flow",
        "",
        "![Feature Flow](feature_flow.png)",
        "",
        "## Files",
        "",
        *[f"- `{path.as_posix()}`" for path in paths],
    ]
    (OUTPUT_DIR / "README.md").write_text("\n".join(report), encoding="utf-8")
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
