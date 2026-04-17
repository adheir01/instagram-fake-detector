"""
Train the fake follower classifier.
Uses XGBoost with cross-validation.
Run: python -m src.model.train
"""
import os
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from src.features.feature_pipeline import FEATURE_COLUMNS

MODEL_PATH = "data/processed/model.joblib"
DATA_PATH = "data/labeled/labeled_profiles.csv"


def load_training_data() -> tuple[pd.DataFrame, pd.Series]:
    """
    Load labeled CSV. Expected columns: all FEATURE_COLUMNS + 'label' (fake/real/suspect).
    See data/labeled/README.md for labeling guide.
    """
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=FEATURE_COLUMNS + ["label"])

    # Replace -1 (not enough data) with median
    for col in FEATURE_COLUMNS:
        if col in df.columns:
            median = df[col][df[col] != -1].median()
            df[col] = df[col].replace(-1, median)

    X = df[FEATURE_COLUMNS]
    # Binary classification: fake=1, real=0 (suspect = fake for training)
    y = df["label"].apply(lambda x: 1 if x in ("fake", "suspect") else 0)
    return X, y


def train_model():
    print("Loading training data...")
    X, y = load_training_data()
    print(f"  {len(X)} samples | {y.sum()} fake | {(~y.astype(bool)).sum()} real")

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
    )

    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc")
    print(f"  CV AUC: {scores.mean():.3f} (+/- {scores.std():.3f})")

    # Final fit on all data
    model.fit(X, y)

    os.makedirs("data/processed", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"  Model saved to {MODEL_PATH}")

    # Feature importance
    importances = pd.Series(model.feature_importances_, index=FEATURE_COLUMNS)
    print("\nTop features:")
    print(importances.sort_values(ascending=False).to_string())


if __name__ == "__main__":
    train_model()
