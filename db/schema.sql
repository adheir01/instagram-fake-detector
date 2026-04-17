-- Instagram Fake Follower Detector — Database Schema

CREATE TABLE IF NOT EXISTS profiles (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(100) UNIQUE NOT NULL,
    full_name       VARCHAR(255),
    follower_count  INTEGER,
    following_count INTEGER,
    post_count      INTEGER,
    is_verified     BOOLEAN DEFAULT FALSE,
    is_private      BOOLEAN DEFAULT FALSE,
    bio             TEXT,
    scraped_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS post_metrics (
    id              SERIAL PRIMARY KEY,
    profile_id      INTEGER REFERENCES profiles(id),
    post_shortcode  VARCHAR(50),
    like_count      INTEGER,
    comment_count   INTEGER,
    posted_at       TIMESTAMP,
    scraped_at      TIMESTAMP DEFAULT NOW()
);

-- Stores known fake signal patterns for the classifier training data
CREATE TABLE IF NOT EXISTS fake_signals (
    id                      SERIAL PRIMARY KEY,
    profile_id              INTEGER REFERENCES profiles(id),
    label                   VARCHAR(10) CHECK (label IN ('fake', 'real', 'suspect')),
    engagement_rate         FLOAT,
    follower_following_ratio FLOAT,
    avg_likes_per_post      FLOAT,
    avg_comments_per_post   FLOAT,
    comment_like_ratio      FLOAT,
    posting_consistency_score FLOAT,   -- std dev of days between posts (lower = more bot-like)
    ghost_follower_estimate FLOAT,     -- % followers with 0 posts
    bio_completeness_score  FLOAT,     -- 0-1, bots often have empty bios
    labeled_by              VARCHAR(50) DEFAULT 'manual',
    labeled_at              TIMESTAMP DEFAULT NOW()
);

-- Stores each analysis run result
CREATE TABLE IF NOT EXISTS analysis_results (
    id              SERIAL PRIMARY KEY,
    profile_id      INTEGER REFERENCES profiles(id),
    fake_score      FLOAT,             -- 0-100, higher = more likely fake
    risk_level      VARCHAR(10) CHECK (risk_level IN ('low', 'medium', 'high')),
    model_version   VARCHAR(20),
    ai_summary      TEXT,              -- Claude-generated narrative
    analyzed_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_profiles_username ON profiles(username);
CREATE INDEX idx_fake_signals_label ON fake_signals(label);
CREATE INDEX idx_results_profile ON analysis_results(profile_id);
