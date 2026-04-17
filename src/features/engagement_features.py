"""
Core feature engineering for fake follower detection.
Each function takes profile + posts data and returns a scalar feature.
"""
import numpy as np
from typing import Optional


def engagement_rate(follower_count: int, avg_likes: float, avg_comments: float) -> float:
    """
    Industry standard: (likes + comments) / followers * 100
    Real accounts: 1-5% for large, 5-15% for micro-influencers
    Fake-inflated: often <0.5% (lots of followers, no engagement)
    Bot-boosted: sometimes >20% (bought likes too)
    """
    if follower_count == 0:
        return 0.0
    return round((avg_likes + avg_comments) / follower_count * 100, 4)


def follower_following_ratio(followers: int, following: int) -> float:
    """
    Real influencers: high ratio (many followers, few following)
    Follow-unfollow bots: ratio close to 1.0 or below
    """
    if following == 0:
        return float(followers)
    return round(followers / following, 4)


def comment_like_ratio(avg_comments: float, avg_likes: float) -> float:
    """
    Organic engagement: ~1 comment per 10-20 likes
    Bought likes only (no comment bots): ratio near 0
    Comment pods: ratio unusually high
    """
    if avg_likes == 0:
        return 0.0
    return round(avg_comments / avg_likes, 4)


def posting_consistency_score(post_timestamps: list) -> float:
    """
    Calculates std deviation of days between posts.
    Low std (very regular) can indicate scheduled bot posting.
    Returns the coefficient of variation (std/mean) — lower = more robotic.
    """
    if len(post_timestamps) < 3:
        return -1.0  # not enough data

    from datetime import datetime
    sorted_ts = sorted(post_timestamps)
    gaps = []
    for i in range(1, len(sorted_ts)):
        if sorted_ts[i] and sorted_ts[i-1]:
            gap = (sorted_ts[i] - sorted_ts[i-1]).total_seconds() / 86400
            gaps.append(gap)

    if not gaps:
        return -1.0

    mean_gap = np.mean(gaps)
    std_gap = np.std(gaps)
    if mean_gap == 0:
        return 0.0
    return round(std_gap / mean_gap, 4)  # CV: lower = more suspicious


def avg_post_metrics(posts: list[dict]) -> tuple[float, float]:
    """Returns (avg_likes, avg_comments) across all posts."""
    if not posts:
        return 0.0, 0.0
    likes = [p.get("like_count", 0) or 0 for p in posts]
    comments = [p.get("comment_count", 0) or 0 for p in posts]
    return round(np.mean(likes), 2), round(np.mean(comments), 2)


def ghost_follower_estimate(followers, post_count, avg_likes):
    if followers == 0 or post_count == 0:
        return 0.0
    
    # Tiered baseline — engagement rate decays naturally at scale
    if followers > 10_000_000:
        expected_rate = 0.001   # 0.1% is normal for mega accounts
    elif followers > 1_000_000:
        expected_rate = 0.005   # 0.5% for large accounts
    elif followers > 100_000:
        expected_rate = 0.015   # 1.5% for mid accounts
    else:
        expected_rate = 0.03    # 3% for small accounts

    actual_rate = avg_likes / followers
    ghost_estimate = max(0, 1 - (actual_rate / expected_rate))
    return round(min(ghost_estimate, 0.99), 4)
