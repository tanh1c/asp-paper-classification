import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import GridSearchCV
import warnings
warnings.filterwarnings('ignore')

# Load data

ROOT_DIR = Path(__file__).resolve().parent.parent
SOI_DIR = Path(__file__).resolve().parent

train_path = SOI_DIR / "Stage_1_publcitrain_with_abstract_only (1).csv"
test_path = ROOT_DIR / 'dataset_stage1' / 'test (2).csv'
output_dir = SOI_DIR / 'best_038_outputs'
output_dir.mkdir(parents=True, exist_ok=True)


def next_submission_path():
    existing_numbers = []
    for path in output_dir.glob('submission_best_038_*.csv'):
        number = path.stem.replace('submission_best_038_', '')
        if number.isdigit():
            existing_numbers.append(int(number))

    next_number = max(existing_numbers, default=0) + 1
    return output_dir / f'submission_best_038_{next_number}.csv'

train_df = pd.read_csv(str(train_path))
test_df = pd.read_csv(str(test_path))

# Clean and Combine text
def preprocess_data(df):
    df = df.copy()
    df['title'] = df['title'].fillna('')
    df['authors'] = df['authors'].fillna('')
    df['venue'] = df['venue'].fillna('unknown')
    df['year'] = df['year'].fillna(2020).astype(int).astype(str)
    if 'abstract' not in df.columns:
        df['abstract_status'] = 'abstract_status_unknown'
    else:
        has_abstract = df['abstract'].notna() & df['abstract'].astype(str).str.strip().ne('')
        df['abstract_status'] = np.where(
            has_abstract,
            'abstract_found_yes',
            'abstract_found_no',
        )
    
    # Give more weight to title and venue by repeating them or just combining
    df['text'] = (
        df['title']
        + " "
        + df['venue']
        + " "
        + df['authors']
        + " "
        + df['year']
        + " "
        + df['abstract_status']
    )
    return df

train_df_c = preprocess_data(train_df)
test_df_c = preprocess_data(test_df)

X_train = train_df_c['text']
y_train = train_df_c['Label'].astype(int)
X_test = test_df_c['text']

# Base vectorizer
tfidf = TfidfVectorizer(sublinear_tf=True, stop_words='english')

# 1. Tune LinearSVC
pipeline_svc = Pipeline([
    ('tfidf', tfidf),
    ('clf', LinearSVC(class_weight='balanced', random_state=42, dual=False))
])
param_grid_svc = {
    'tfidf__ngram_range': [(1, 2), (1, 3)],
    'tfidf__max_features': [20000, 50000],
    'tfidf__min_df': [1, 2],
    'clf__C': [0.1, 0.5, 1.0, 2.0]
}
grid_svc = GridSearchCV(pipeline_svc, param_grid_svc, cv=5, scoring='f1_macro', n_jobs=1)
grid_svc.fit(X_train, y_train)
print(f"Best SVC CV F1: {grid_svc.best_score_:.4f}")

# 2. Tune Logistic Regression
pipeline_lr = Pipeline([
    ('tfidf', tfidf),
    ('clf', LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000, solver='saga'))
])
param_grid_lr = {
    'tfidf__ngram_range': [(1, 2), (1, 3)],
    'tfidf__max_features': [20000, 50000],
    'tfidf__min_df': [1, 2],
    'clf__C': [1.0, 5.0, 10.0]
}
grid_lr = GridSearchCV(pipeline_lr, param_grid_lr, cv=5, scoring='f1_macro', n_jobs=1)
grid_lr.fit(X_train, y_train)
print(f"Best LR CV F1: {grid_lr.best_score_:.4f}")

# 3. Create a Voting Classifier using the best tuned estimators
best_svc = grid_svc.best_estimator_
best_lr = grid_lr.best_estimator_

# For MNB, we can't easily use sublinear_tf with negative values if any, but TFIDF is non-negative
pipeline_mnb = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_features=30000, sublinear_tf=True, min_df=1, stop_words='english')),
    ('clf', MultinomialNB())
])
pipeline_mnb.fit(X_train, y_train) # train it just in case

# Combine in Soft Voting for LR & MNB, but SVC doesn't predict_proba naturally unless wrapped. 
# We will use Hard Voting across SVC, LR, and MNB
ensemble = VotingClassifier(estimators=[
    ('svc', best_svc),
    ('lr', best_lr),
    ('mnb', pipeline_mnb)
], voting='hard')

# Train Ensemble
from sklearn.model_selection import cross_val_score
ensemble_cv = cross_val_score(ensemble, X_train, y_train, cv=5, scoring='f1_macro')
print(f"Ensemble CV F1: {np.mean(ensemble_cv):.4f}")

# Choose the absolute best model
best_overall = best_svc
best_score = grid_svc.best_score_

if grid_lr.best_score_ > best_score:
    best_overall = best_lr
    best_score = grid_lr.best_score_
    
if np.mean(ensemble_cv) > best_score:
    best_overall = ensemble
    best_score = np.mean(ensemble_cv)

print(f"\nProceeding with best model CV Score: {best_score:.4f}")

# Train the best overall on full data
best_overall.fit(X_train, y_train)
test_predictions = best_overall.predict(X_test)

# Create submission
submission = pd.DataFrame({
    'id': test_df['id'],
    'Label': test_predictions
})

submission_path = next_submission_path()
submission.to_csv(submission_path, index=False)

print("\n--- NEW PREDICTIONS ---")
print(submission.to_csv(index=False))
print(f"\nSaved submission to: {submission_path}")
