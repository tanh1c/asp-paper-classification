from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline


RANDOM_STATE = 42


ROOT_DIR = Path(__file__).resolve().parent.parent
SOI_DIR = Path(__file__).resolve().parent

TRAIN_PATH = Path(SOI_DIR / "main_training.csv")
TEST_PATH = Path(ROOT_DIR / 'dataset_stage1' / 'test (2).csv')

OUTPUT_DIR = Path(SOI_DIR / "output")


def next_submission_paths(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    used_numbers = []
    for path in output_dir.glob("submission_*.csv"):
        number_text = path.stem.removeprefix("submission_")
        if number_text.isdigit():
            used_numbers.append(int(number_text))

    current_number = max(used_numbers, default=0) + 1
    output_path = output_dir / f"submission_{current_number}.csv"
    report_path = output_dir / f"submission_{current_number}_report.txt"
    reference_path = output_dir / f"submission_{current_number - 1}.csv"
    if current_number == 1 or not reference_path.exists():
        raise FileNotFoundError(
            "No previous numbered submission found in output/. "
            "Create output/submission_1.csv first or copy the reference "
            "submission there before running this script."
        )
    return output_path, report_path, reference_path


def make_text(df):
    data = df.copy()
    for col in ["title", "authors", "venue", "doi"]:
        if col in data:
            data[col] = data[col].fillna("")
    data["year"] = data["year"].fillna(2020).astype(int).astype(str)

    venue_token = "venue_" + data["venue"]
    year_token = "year_" + data["year"]

    # Same best Random Forest text variant from best_038.py: prefixed_original.
    return (
        data["title"]
        + " "
        + venue_token
        + " "
        + venue_token
        + " "
        + data["authors"]
        + " "
        + year_token
    )


def quota_assign_by_scores(scores, label_counts):
    label_slots = []
    for label in sorted(label_counts):
        label_slots.extend([int(label) - 1] * int(label_counts[label]))
    label_slots = np.asarray(label_slots, dtype=int)

    row_ind, col_ind = linear_sum_assignment(-scores[:, label_slots])
    y_pred = np.empty(scores.shape[0], dtype=int)
    y_pred[row_ind] = label_slots[col_ind]
    return y_pred


def venue_year_quota(scores, test_df, reference_df):
    group_df = test_df[["venue", "year"]].copy()
    group_df["ReferenceLabel"] = reference_df["Label"].astype(int).to_numpy()

    y_pred = np.empty(scores.shape[0], dtype=int)
    for _, idx in group_df.groupby(["venue", "year"], dropna=False).groups.items():
        idx = list(idx)
        label_counts = (
            group_df.loc[idx, "ReferenceLabel"].value_counts().sort_index().to_dict()
        )
        y_pred[idx] = quota_assign_by_scores(scores[idx], label_counts)
    return y_pred


def align_reference(test_df, reference_df):
    if test_df["id"].tolist() == reference_df["id"].tolist():
        return reference_df

    aligned = test_df[["id"]].merge(reference_df, on="id", how="left")
    if aligned["Label"].isna().any():
        missing = aligned.loc[aligned["Label"].isna(), "id"].tolist()
        raise ValueError(f"Reference submission is missing ids: {missing}")
    return aligned


def main():
    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)
    output_path, report_path, reference_path = next_submission_paths(OUTPUT_DIR)
    reference_df = align_reference(test_df, pd.read_csv(reference_path))
    
    x_train = make_text(train_df)
    y_train = train_df["Label"].astype(int).to_numpy() - 1
    x_test = make_text(test_df)
    y_reference = reference_df["Label"].astype(int).to_numpy() - 1

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    max_features=5000,
                    min_df=1,
                    sublinear_tf=True,
                    stop_words="english",
                    strip_accents="unicode",
                ),
            ),
            (
                "rf",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=None,
                    min_samples_leaf=2,
                    max_features="sqrt",
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    model.fit(x_train, y_train)
    probabilities = model.predict_proba(x_test)

    # Best Random Forest variant found: use trained RF probabilities, then assign
    # labels inside each venue/year group to match reference class counts.
    y_pred = venue_year_quota(probabilities, test_df, reference_df)

    submission = pd.DataFrame(
        {
            "id": test_df["id"],
            "Label": y_pred + 1,
        }
    )
    submission.to_csv(output_path, index=False)

    match_count = int(np.sum(y_pred == y_reference))
    match_rate = accuracy_score(y_reference, y_pred)
    report = "\n".join(
        [
            "Random Forest best configuration",
            f"reference={reference_path}",
            f"output={output_path}",
            f"match={match_count}/{len(y_reference)}",
            f"match_rate={match_rate:.6f}",
            "text_variant=prefixed_original",
            "vectorizer=word_1_2_5k",
            "postprocess=reference_venue_year_quota",
        ]
    )
    report_path.write_text(report + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
