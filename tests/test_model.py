"""Tests for the prediction layer."""
import pytest
from src.model.predict import predict, PredictionResult, _interpret_signals


FAKE_FEATURES = {
    "engagement_rate": 0.08,
    "follower_following_ratio": 0.95,
    "comment_like_ratio": 0.001,
    "posting_consistency_cv": 0.05,
    "ghost_follower_estimate": 0.81,
    "bio_completeness": 0.0,
    "avg_likes_per_post": 45,
    "avg_comments_per_post": 1,
    "follower_count_log": 11.5,
    "is_verified": 0,
}

REAL_FEATURES = {
    "engagement_rate": 4.2,
    "follower_following_ratio": 18.5,
    "comment_like_ratio": 0.07,
    "posting_consistency_cv": 0.65,
    "ghost_follower_estimate": 0.12,
    "bio_completeness": 0.9,
    "avg_likes_per_post": 850,
    "avg_comments_per_post": 60,
    "follower_count_log": 9.7,
    "is_verified": 0,
}


def test_signal_interpretation_fake():
    signals = _interpret_signals(FAKE_FEATURES, 85)
    flags = [s["flag"] for s in signals]
    assert "red" in flags


def test_signal_interpretation_real():
    signals = _interpret_signals(REAL_FEATURES, 12)
    flags = [s["flag"] for s in signals]
    assert "green" in flags


def test_prediction_result_structure():
    # Test without real model — just signal interpretation
    signals = _interpret_signals(FAKE_FEATURES, 80)
    assert all("signal" in s and "value" in s and "flag" in s for s in signals)


def test_high_ghost_flagged():
    signals = _interpret_signals(FAKE_FEATURES, 80)
    signal_names = [s["signal"] for s in signals]
    assert any("ghost" in name.lower() for name in signal_names)
