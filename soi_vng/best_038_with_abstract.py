import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import VotingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

warnings.filterwarnings("ignore")


ROOT_DIR = Path(__file__).resolve().parent.parent
SOI_DIR = Path(__file__).resolve().parent

train_path = SOI_DIR / "Stage_1_publcitrain_final_clean.csv"
test_path = ROOT_DIR / "dataset_stage1" / "test_with_abstract.csv"
output_dir = SOI_DIR / "best_038_with_abstract_outputs"
output_dir.mkdir(parents=True, exist_ok=True)


def next_submission_path():
    existing_numbers = []
    for path in output_dir.glob("submission_best_038_with_abstract_*.csv"):
        number = path.stem.replace("submission_best_038_with_abstract_", "")
        if number.isdigit():
            existing_numbers.append(int(number))

    next_number = max(existing_numbers, default=0) + 1
    return output_dir / f"submission_best_038_with_abstract_{next_number}.csv"


def clean_year(series):
    year = pd.to_numeric(series, errors="coerce").fillna(2020).astype(int)
    return year.astype(str)


def clean_abstract(df):
    if "abstract" not in df.columns:
        return pd.Series("<unknown>", index=df.index)

    abstract = df["abstract"].fillna("").astype(str).str.strip()
    return abstract.mask(abstract.eq(""), "<unknown>")


def preprocess_data(df):
    df = df.copy()
    df["title"] = df["title"].fillna("")
    df["authors"] = df["authors"].fillna("")
    df["venue"] = df["venue"].fillna("unknown")
    df["year"] = clean_year(df["year"])
    df["abstract_text"] = clean_abstract(df)

    df["text"] = (
        df["title"]
        + " "
        + df["venue"]
        + " "
        + df["authors"]
        + " "
        + df["year"]
        + " "
        + df["abstract_text"]
    )
    return df


train_df = pd.read_csv(str(train_path))
test_df = pd.read_csv(str(test_path))

train_df_c = preprocess_data(train_df)
test_df_c = preprocess_data(test_df)

X_train = train_df_c["text"]
y_train = train_df_c["Label"].astype(int)
X_test = test_df_c["text"]

tfidf = TfidfVectorizer(sublinear_tf=True, stop_words="english")

pipeline_svc = Pipeline(
    [
        ("tfidf", tfidf),
        ("clf", LinearSVC(class_weight="balanced", random_state=42, dual=False)),
    ]
)
param_grid_svc = {
    "tfidf__ngram_range": [(1, 2), (1, 3)],
    "tfidf__max_features": [20000, 50000],
    "tfidf__min_df": [1, 2],
    "clf__C": [0.1, 0.5, 1.0, 2.0],
}
grid_svc = GridSearchCV(
    pipeline_svc, param_grid_svc, cv=5, scoring="f1_macro", n_jobs=1
)
grid_svc.fit(X_train, y_train)
print(f"Best SVC CV F1: {grid_svc.best_score_:.4f}")

pipeline_lr = Pipeline(
    [
        ("tfidf", tfidf),
        (
            "clf",
            LogisticRegression(
                class_weight="balanced",
                random_state=42,
                max_iter=1000,
                solver="saga",
            ),
        ),
    ]
)
param_grid_lr = {
    "tfidf__ngram_range": [(1, 2), (1, 3)],
    "tfidf__max_features": [20000, 50000],
    "tfidf__min_df": [1, 2],
    "clf__C": [1.0, 5.0, 10.0],
}
grid_lr = GridSearchCV(
    pipeline_lr, param_grid_lr, cv=5, scoring="f1_macro", n_jobs=1
)
grid_lr.fit(X_train, y_train)
print(f"Best LR CV F1: {grid_lr.best_score_:.4f}")

best_svc = grid_svc.best_estimator_
best_lr = grid_lr.best_estimator_

pipeline_mnb = Pipeline(
    [
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=30000,
                sublinear_tf=True,
                min_df=1,
                stop_words="english",
            ),
        ),
        ("clf", MultinomialNB()),
    ]
)
pipeline_mnb.fit(X_train, y_train)

ensemble = VotingClassifier(
    estimators=[
        ("svc", best_svc),
        ("lr", best_lr),
        ("mnb", pipeline_mnb),
    ],
    voting="hard",
)

ensemble_cv = cross_val_score(ensemble, X_train, y_train, cv=5, scoring="f1_macro")
print(f"Ensemble CV F1: {np.mean(ensemble_cv):.4f}")

best_overall = best_svc
best_score = grid_svc.best_score_

if grid_lr.best_score_ > best_score:
    best_overall = best_lr
    best_score = grid_lr.best_score_

if np.mean(ensemble_cv) > best_score:
    best_overall = ensemble
    best_score = np.mean(ensemble_cv)

print(f"\nProceeding with best model CV Score: {best_score:.4f}")

best_overall.fit(X_train, y_train)
test_predictions = best_overall.predict(X_test)

submission = pd.DataFrame(
    {
        "id": test_df["id"],
        "Label": test_predictions,
    }
)

submission_path = next_submission_path()
submission.to_csv(submission_path, index=False)

print("\n--- NEW PREDICTIONS ---")
print(submission.to_csv(index=False))
print(f"\nSaved submission to: {submission_path}")
