"""
Orchestrates feature extraction from parsed profile + posts
into a single flat dict ready for the ML model.
"""
from src.features.engagement_features import (
    engagement_rate, follower_following_ratio, comment_like_ratio,
    posting_consistency_score, avg_post_metrics, ghost_follower_estimate
)
from src.scraper.profile_parser import parse_bio_completeness


def build_feature_vector(profile: dict, posts: list[dict], raw: dict = None) -> dict:
    """
    Takes clean profile dict + list of post dicts.
    Returns flat feature dict for model input.
    """
    avg_likes, avg_comments = avg_post_metrics(posts)
    followers = profile.get("follower_count", 0)
    following = profile.get("following_count", 0)
    post_timestamps = [p.get("posted_at") for p in posts]

    features = {
        "engagement_rate": engagement_rate(followers, avg_likes, avg_comments),
        "follower_following_ratio": follower_following_ratio(followers, following),
        "comment_like_ratio": comment_like_ratio(avg_comments, avg_likes),
        "posting_consistency_cv": posting_consistency_score(post_timestamps),
        "ghost_follower_estimate": ghost_follower_estimate(
            followers, profile.get("post_count", 0), avg_likes
        ),
        "bio_completeness": parse_bio_completeness(raw) if raw else 0.5,
        "avg_likes_per_post": avg_likes,
        "avg_comments_per_post": avg_comments,
        "follower_count_log": __import__('math').log1p(followers),
        "is_verified": int(profile.get("is_verified", False)),
    }
    return features


FEATURE_COLUMNS = [
    "engagement_rate",
    "follower_following_ratio",
    "comment_like_ratio",
    "posting_consistency_cv",
    "ghost_follower_estimate",
    "bio_completeness",
    "avg_likes_per_post",
    "avg_comments_per_post",
    "follower_count_log",
    "is_verified",
]
