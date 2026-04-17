"""
Prediction logic. Takes a feature vector, returns a FakeScore (0-100)
and a risk level.
"""
import joblib
import numpy as np
import pandas as pd
from dataclasses import dataclass
from src.features.feature_pipeline import FEATURE_COLUMNS

MODEL_PATH = "data/processed/model.joblib"
_model = None


def _load_model():
    global _model
    if _model is None:
        try:
            _model = joblib.load(MODEL_PATH)
        except FileNotFoundError:
            return None
        except Exception:
            return None
    return _model


@dataclass
class PredictionResult:
    fake_score: float       # 0-100
    risk_level: str         # low / medium / high
    probability_fake: float # raw model probability
    top_signals: list[dict] # which features drove the score


def predict(feature_vector: dict) -> PredictionResult:
    model = _load_model()

    if model is None:
        score = _rule_based_score(feature_vector)
        signals = _interpret_signals(feature_vector, score)
        risk_level = "high" if score >= 70 else "medium" if score >= 40 else "low"
        return PredictionResult(
            fake_score=score,
            risk_level=risk_level,
            probability_fake=score / 100,
            top_signals=signals,
        )

    row = {col: feature_vector.get(col, 0) for col in FEATURE_COLUMNS}
    X = pd.DataFrame([row])
    prob_fake = float(model.predict_proba(X)[0][1])
    fake_score = round(prob_fake * 100, 1)
    risk_level = "high" if fake_score >= 70 else "medium" if fake_score >= 40 else "low"
    signals = _interpret_signals(feature_vector, fake_score)
    return PredictionResult(
        fake_score=fake_score,
        risk_level=risk_level,
        probability_fake=prob_fake,
        top_signals=signals,
    )


def _interpret_signals(features: dict, score: float) -> list[dict]:
    """Human-readable signal breakdown for the Streamlit UI."""
    signals = []

    er = features.get("engagement_rate", 0)
    followers = features.get("follower_count_log", 0)

    # Adjust thresholds based on account size
    if followers > 16:        # log(10M) ≈ 16
        low_threshold = 0.05
    elif followers > 13:      # log(1M) ≈ 13
        low_threshold = 0.2
    else:
        low_threshold = 0.5

    if er < low_threshold:
        signals.append({"signal": "Very low engagement rate", "value": f"{er:.2f}%", "flag": "red"})
    elif er > 20:
        signals.append({"signal": "Suspiciously high engagement", "value": f"{er:.2f}%", "flag": "orange"})
    else:
        signals.append({"signal": "Normal engagement rate", "value": f"{er:.2f}%", "flag": "green"})

    ratio = features.get("follower_following_ratio", 1)
    if ratio < 0.5:
        signals.append({"signal": "Follow/unfollow pattern detected", "value": f"{ratio:.2f}x", "flag": "red"})

    ghost = features.get("ghost_follower_estimate", 0)
    if ghost > 0.6:
        signals.append({"signal": "High ghost follower estimate", "value": f"{ghost*100:.0f}%", "flag": "red"})
    elif ghost > 0.3:
        signals.append({"signal": "Moderate ghost followers", "value": f"{ghost*100:.0f}%", "flag": "orange"})

    cv = features.get("posting_consistency_cv", -1)
    if 0 <= cv < 0.2:
        signals.append({"signal": "Robot-like posting schedule", "value": f"CV={cv:.2f}", "flag": "orange"})

    bio = features.get("bio_completeness", 0)
    if bio < 0.3:
        signals.append({"signal": "Incomplete profile bio", "value": f"{bio*100:.0f}% complete", "flag": "orange"})

    return signals


def _rule_based_score(features: dict) -> float:
    score = 0.0
    er = features.get("engagement_rate", 0)
    if er < 0.3:    score += 35
    elif er < 0.8:  score += 20
    ratio = features.get("follower_following_ratio", 10)
    if ratio < 1.1:  score += 25
    elif ratio < 2:  score += 10
    score += features.get("ghost_follower_estimate", 0) * 25
    if features.get("bio_completeness", 1) < 0.1: score += 15
    return round(min(score, 100), 1)
