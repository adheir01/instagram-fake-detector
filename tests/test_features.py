"""Tests for feature engineering functions."""
import pytest
from src.features.engagement_features import (
    engagement_rate, follower_following_ratio,
    comment_like_ratio, ghost_follower_estimate,
    posting_consistency_score
)
from datetime import datetime, timedelta


def test_engagement_rate_typical_real():
    # 10k followers, 300 avg likes, 15 avg comments → ~3.15%
    rate = engagement_rate(10000, 300, 15)
    assert 3.0 < rate < 3.5


def test_engagement_rate_zero_followers():
    assert engagement_rate(0, 100, 10) == 0.0


def test_engagement_rate_fake_profile():
    # 100k followers but only 50 likes — very suspicious
    rate = engagement_rate(100000, 50, 2)
    assert rate < 0.1


def test_follower_following_ratio_influencer():
    # Real influencer: 50k followers, 500 following
    ratio = follower_following_ratio(50000, 500)
    assert ratio == 100.0


def test_follower_following_ratio_bot():
    # Follow/unfollow bot: nearly 1:1
    ratio = follower_following_ratio(5000, 4800)
    assert ratio < 1.1


def test_comment_like_ratio_organic():
    # ~1 comment per 15 likes is healthy
    ratio = comment_like_ratio(20, 300)
    assert 0.05 < ratio < 0.1


def test_comment_like_ratio_bought_likes():
    # Bought likes, no comments
    ratio = comment_like_ratio(2, 5000)
    assert ratio < 0.001


def test_ghost_follower_high():
    # 100k followers, 0 posts, 10 avg likes → very high ghost estimate
    estimate = ghost_follower_estimate(100000, 50, 10)
    assert estimate > 0.8


def test_ghost_follower_low():
    # 10k followers, 300 avg likes → healthy engagement
    estimate = ghost_follower_estimate(10000, 50, 300)
    assert estimate < 0.2


def test_posting_consistency_robotic():
    # Posts exactly every 3 days — very low CV = suspicious
    base = datetime(2024, 1, 1)
    timestamps = [base + timedelta(days=3*i) for i in range(10)]
    cv = posting_consistency_score(timestamps)
    assert 0 <= cv < 0.15


def test_posting_consistency_human():
    # Irregular posting — higher CV = more human
    import random
    random.seed(42)
    base = datetime(2024, 1, 1)
    timestamps = [base + timedelta(days=random.randint(1, 14)) * i for i in range(1, 10)]
    cv = posting_consistency_score(timestamps)
    assert cv > 0.2


def test_posting_consistency_insufficient_data():
    timestamps = [datetime(2024, 1, 1)]
    assert posting_consistency_score(timestamps) == -1.0
