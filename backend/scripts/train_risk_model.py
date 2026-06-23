"""Train the at-risk student detector (Brique IA 4).

PIPELINE
========
1. Load the dataset (app/data/risk_training_data.csv).
2. Standardise the 8 features (StandardScaler) so they are comparable.
3. Train a Logistic Regression classifier.
4. Evaluate it: accuracy, precision, recall, F1 and ROC-AUC on a held-out
   test set + 5-fold cross-validation. For an EARLY-WARNING system, RECALL
   on the at-risk class matters most (we prefer to catch a struggling
   student even at the cost of a few false alarms).
5. Save the model bundle to app/data/risk_model.joblib.

WHY LOGISTIC REGRESSION + STANDARDISATION?
It is interpretable: the standardised coefficients tell us which factor
pushes a student towards "at risk". That lets the service explain WHY a
student is flagged (top factors), which is essential for a teacher tool.

Run:  python scripts/train_risk_model.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, classification_report,
                             roc_auc_score)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

DATA = Path(__file__).resolve().parents[1] / "app" / "data" / "risk_training_data.csv"
OUT = Path(__file__).resolve().parents[1] / "app" / "data" / "risk_model.joblib"


def load():
    with DATA.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        features = header[:-1]
        X, y = [], []
        for row in reader:
            X.append([float(v) for v in row[:-1]])
            y.append(int(row[-1]))
    return np.array(X), np.array(y), features


def main() -> None:
    X, y, features = load()
    print(f"Loaded {len(y)} students, {len(features)} features, "
          f"{int(y.sum())} at risk")

    scaler = StandardScaler().fit(X)
    Xs = scaler.transform(X)

    X_tr, X_te, y_tr, y_te = train_test_split(
        Xs, y, test_size=0.2, random_state=42, stratify=y)
    clf = LogisticRegression(max_iter=2000, class_weight="balanced")
    clf.fit(X_tr, y_tr)

    y_pred = clf.predict(X_te)
    y_proba = clf.predict_proba(X_te)[:, 1]
    print(f"\nTest accuracy : {accuracy_score(y_te, y_pred):.3f}")
    print(f"ROC-AUC       : {roc_auc_score(y_te, y_proba):.3f}")
    print("\nReport (class 1 = at risk):")
    print(classification_report(y_te, y_pred, target_names=["ok", "at_risk"],
                                zero_division=0))
    cv = cross_val_score(clf, Xs, y, cv=5, scoring="accuracy")
    print(f"5-fold CV accuracy: {cv.mean():.3f} (+/- {cv.std():.3f})")

    # Which factors push towards "at risk"? (standardised coefficients)
    print("\nFactor influence (standardised coefficients):")
    for name, coef in sorted(zip(features, clf.coef_[0]),
                             key=lambda kv: -abs(kv[1])):
        arrow = "raises risk" if coef > 0 else "lowers risk"
        print(f"  {name:18s} {coef:+.2f}  ({arrow})")

    # Retrain on all data before saving.
    clf_full = LogisticRegression(max_iter=2000, class_weight="balanced").fit(Xs, y)
    bundle = {
        "scaler": scaler,
        "clf": clf_full,
        "features": features,
        "threshold": 0.50,
    }
    joblib.dump(bundle, OUT)
    print(f"\nSaved model -> {OUT}")


if __name__ == "__main__":
    main()
