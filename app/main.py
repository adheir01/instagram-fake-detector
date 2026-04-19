"""
Streamlit app — Instagram Fake Follower Detector
Run: streamlit run app/main.py
"""
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.scraper.apify_scraper import scrape_profile
from src.scraper.profile_parser import parse_profile, parse_posts
from src.features.feature_pipeline import build_feature_vector
from src.model.predict import predict
from src.services.llm_analyzer import generate_summary
from src.services.pdf_report import generate_pdf_report
from app.components import render_score_gauge, render_signal_cards, render_profile_stats

st.set_page_config(
    page_title="Fake Follower Detector",
    page_icon="🔍",
    layout="centered"
)

st.title("Instagram Fake Follower Detector")
st.caption("Built by Tobi Kazeem · Helps sponsors identify genuine influencer audiences")

st.divider()

username_input = st.text_input(
    "Instagram username",
    placeholder="Enter username (without @)",
    help="Public profiles only. Analysis takes ~60 seconds due to scraping."
)

col1, col2 = st.columns([2, 1])
with col1:
    analyze_btn = st.button("Analyze Profile", type="primary", use_container_width=True)
with col2:
    demo_btn = st.button("Try Demo Data", use_container_width=True)

if demo_btn:
    with st.spinner("Loading fixture data..."):
        from src.scraper.apify_scraper import scrape_profile_local, scrape_posts_local
        from src.scraper.profile_parser import parse_profile, parse_posts, parse_bio_completeness
        from src.features.feature_pipeline import build_feature_vector

        raw_profile = scrape_profile_local()
        raw_posts   = scrape_posts_local()

        profile  = parse_profile(raw_profile)
        posts    = parse_posts(raw_posts)
        features = build_feature_vector(profile, posts, raw_profile)

        st.session_state["username"] = profile["username"]
        st.session_state["profile"]  = profile
        st.session_state["posts"]    = posts
        st.session_state["features"] = features

if analyze_btn and username_input:
    with st.spinner(f"Scraping @{username_input} via Apify... (~90s)"):
        from src.scraper.apify_scraper import scrape_posts

        raw_profile = scrape_profile(username_input)
        if not raw_profile:
            st.error("Could not fetch profile. Check the username or your Apify token.")
            st.stop()

        st.spinner("Fetching posts...")
        raw_posts = scrape_posts(username_input, limit=12)

        profile  = parse_profile(raw_profile)
        posts    = parse_posts(raw_posts)
        features = build_feature_vector(profile, posts, raw_profile)

        st.session_state["username"] = username_input
        st.session_state["profile"]  = profile
        st.session_state["posts"]    = posts
        st.session_state["features"] = features
        st.session_state["demo_mode"] = False

if "features" in st.session_state:
    features = st.session_state["features"]
    profile = st.session_state["profile"]
    username = st.session_state["username"]
    posts = st.session_state.get("posts", [])

    result = predict(features)

    st.subheader(f"Results for @{username}")
    render_score_gauge(result.fake_score, result.risk_level)
    render_profile_stats(profile, features)
    render_signal_cards(result.top_signals)

    st.divider()
    st.subheader("AI Sponsor Recommendation")

    if st.button("Generate AI Summary"):
        with st.spinner("Asking Claude..."):
            summary = generate_summary(username, profile, features, result)
            st.session_state["ai_summary"] = summary

    if "ai_summary" in st.session_state:
        st.info(st.session_state["ai_summary"])

        pdf_bytes = generate_pdf_report(
            username, profile, features, result, st.session_state["ai_summary"]
        )
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=f"{username}_authenticity_report.pdf",
            mime="application/pdf"
        )

st.divider()
st.caption("Methodology: engagement rate analysis · follower/following ratio · ghost follower estimation · posting pattern analysis · XGBoost classifier")
