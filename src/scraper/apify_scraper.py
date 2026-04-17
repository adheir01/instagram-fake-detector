import os
import json
import time
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN   = os.getenv("APIFY_API_TOKEN")
BASE_URL      = "https://api.apify.com/v2"
PROFILE_ACTOR = "apify~instagram-profile-scraper"
POSTS_ACTOR   = "instagram-scraper~fast-instagram-post-scraper"
FIXTURES_DIR  = "data/fixtures"


def _run_actor(actor_id: str, payload: dict) -> Optional[list]:
    params   = {"token": APIFY_TOKEN}
    response = requests.post(f"{BASE_URL}/acts/{actor_id}/runs",
                             json=payload, params=params)
    response.raise_for_status()
    run_id = response.json()["data"]["id"]

    for _ in range(40):
        time.sleep(5)
        r      = requests.get(f"{BASE_URL}/actor-runs/{run_id}", params=params)
        status = r.json()["data"]["status"]
        if status == "SUCCEEDED":
            dataset_id = r.json()["data"]["defaultDatasetId"]
            return requests.get(f"{BASE_URL}/datasets/{dataset_id}/items",
                                params=params).json()
        if status in ("FAILED", "ABORTED"):
            return None
    return None


def scrape_profile(username: str) -> Optional[dict]:
    if not APIFY_TOKEN:
        raise ValueError("APIFY_API_TOKEN not set in .env")
    items = _run_actor(PROFILE_ACTOR, {"usernames": [username]})
    return items[0] if items else None


def scrape_posts(username: str, limit: int = 12) -> list:
    if not APIFY_TOKEN:
        raise ValueError("APIFY_API_TOKEN not set in .env")
    items = _run_actor(POSTS_ACTOR, {
        "instagramUsernames": [username],
        "postsPerProfile": limit,
        "retries": 3
    })
    return items or []


def scrape_profile_local() -> Optional[dict]:
    path = f"{FIXTURES_DIR}/sample_profile.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data[0] if isinstance(data, list) else data


def scrape_posts_local() -> list:
    path = f"{FIXTURES_DIR}/sample_posts.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)