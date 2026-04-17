"""
Model evaluation utilities.
Run after training to get a full performance report.
Usage: python -m src.model.evaluate
"""
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report, roc_auc_score,
    ConfusionMatrixDisplay, RocCurveDisplay
)
from sklearn.model_selection import train_test_split
from src.features.feature_pipeline import FEATURE_COLUMNS

MODEL_PATH = "data/processed/model.joblib"
DATA_PATH = "data/labeled/labeled_profiles.csv"


def evaluate():
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=FEATURE_COLUMNS + ["label"])

    X = df[FEATURE_COLUMNS].replace(-1, df[FEATURE_COLUMNS].median())
    y = df["label"].apply(lambda x: 1 if x in ("fake", "suspect") else 0)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = joblib.load(MODEL_PATH)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    print("=== Classification Report ===")
    print(classification_report(y_test, y_pred, target_names=["real", "fake"]))
    print(f"ROC AUC: {roc_auc_score(y_test, y_prob):.4f}")

    # Save plots
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    ConfusionMatrixDisplay.from_predictions(y_test, y_pred,
        display_labels=["real", "fake"], ax=axes[0], colorbar=False)
    axes[0].set_title("Confusion Matrix")

    RocCurveDisplay.from_predictions(y_test, y_prob, ax=axes[1])
    axes[1].set_title("ROC Curve")

    plt.tight_layout()
    plt.savefig("docs/model_evaluation.png", dpi=150)
    print("Plots saved to docs/model_evaluation.png")


if __name__ == "__main__":
    evaluate()
