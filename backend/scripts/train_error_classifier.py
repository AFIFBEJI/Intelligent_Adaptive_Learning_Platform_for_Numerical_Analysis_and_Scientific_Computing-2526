"""Train the error-type classifier (Brique IA 3).

WHAT IT DOES
============
1. Loads the labelled dataset (app/data/error_training_data.json).
2. Turns each text into features:
     - PRIMARY: semantic embeddings (reuses Brique IA 2, sentence-transformers)
     - FALLBACK: TF-IDF (classic NLP, no heavy model needed)
3. Trains a Logistic Regression classifier (scikit-learn).
4. Evaluates it on a held-out test set (accuracy + per-class report) and
   with 5-fold cross-validation.
5. Saves the trained model bundle to app/data/error_classifier.joblib.

WHY LOGISTIC REGRESSION?
It is a simple, fast, interpretable linear classifier that works very well
on top of good text features. It is the standard baseline for text
classification and is easy to defend in a PFE.

Run:  python scripts/train_error_classifier.py
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, classification_report

DATA = Path(__file__).resolve().parents[1] / "app" / "data" / "error_training_data.json"
OUT = Path(__file__).resolve().parents[1] / "app" / "data" / "error_classifier.joblib"
THRESHOLD = 0.30  # below this max-probability -> "unknown"


def load_data():
    rows = json.loads(DATA.read_text(encoding="utf-8"))
    return [r["text"] for r in rows], [r["code"] for r in rows]


def build_features(texts):
    """Return (X, method, vectorizer). Try embeddings, else TF-IDF."""
    try:
        from app.services import embedding_service
        if embedding_service.is_available():
            print("Features: semantic embeddings (Brique IA 2)")
            X = np.vstack([embedding_service.encode(t) for t in texts])
            return X, "embeddings", None
    except Exception as exc:  # noqa: BLE001
        print(f"Embeddings unavailable ({exc}); using TF-IDF.")
    print("Features: TF-IDF (1-2 grams)")
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, lowercase=True)
    X = vec.fit_transform(texts)
    return X, "tfidf", vec


def main() -> None:
    texts, labels = load_data()
    print(f"Loaded {len(texts)} examples, {len(set(labels))} classes")

    X, method, vec = build_features(texts)
    y = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf = LogisticRegression(max_iter=2000, C=4.0)
    clf.fit(X_train, y_train)

    # Evaluation
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nHeld-out test accuracy: {acc:.3f}")
    print("\nPer-class report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    cv = cross_val_score(clf, X, y, cv=5)
    print(f"5-fold CV accuracy: {cv.mean():.3f} (+/- {cv.std():.3f})")

    # Retrain on ALL data before saving (use every example)
    clf_full = LogisticRegression(max_iter=2000, C=4.0)
    clf_full.fit(X, y)

    bundle = {
        "method": method,
        "vectorizer": vec,          # None for embeddings
        "clf": clf_full,
        "classes": list(clf_full.classes_),
        "threshold": THRESHOLD,
        "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2" if method == "embeddings" else None,
    }
    joblib.dump(bundle, OUT)
    print(f"\nSaved model -> {OUT}  (method={method})")


if __name__ == "__main__":
    main()
