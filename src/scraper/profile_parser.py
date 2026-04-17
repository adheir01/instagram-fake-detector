from datetime import datetime


def parse_profile(raw: dict) -> dict:
    return {
        "username":        raw.get("username", ""),
        "full_name":       raw.get("fullName", ""),
        "follower_count":  raw.get("followersCount", 0) or 0,
        "following_count": raw.get("followsCount", 0) or 0,
        "post_count":      raw.get("postsCount", 0) or 0,
        "is_verified":     raw.get("verified", False),
        "is_private":      raw.get("private", False),
        "bio":             raw.get("biography", ""),
        "external_url":    raw.get("externalUrl", ""),
    }


def parse_posts(posts_raw: list) -> list:
    """
    Parses post data from instagram-scraper/fast-instagram-post-scraper.
    Each post has like_count, comment_count, date, user.username.
    """
    parsed = []
    for post in posts_raw:
        ts = post.get("date")
        parsed.append({
            "post_shortcode": post.get("shortcode", ""),
            "like_count":     post.get("like_count", 0) or 0,
            "comment_count":  post.get("comment_count", 0) or 0,
            "posted_at":      datetime.fromisoformat(
                                  ts.replace("Z", "+00:00")
                              ) if ts else None,
            "username":       post.get("user", {}).get("username", ""),
        })
    return parsed


def parse_bio_completeness(raw: dict) -> float:
    """
    Scores 0-1 how complete a profile is.
    Uses danek field names.
    """
    score = 0.0
    if raw.get("full_name"):                                    score += 0.3
    if raw.get("biography") and len(raw["biography"]) > 20:    score += 0.4
    if raw.get("external_url"):                                 score += 0.3
    return round(score, 2)