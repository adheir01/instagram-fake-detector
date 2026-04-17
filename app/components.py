"""
Reusable Streamlit UI components.
"""
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def render_score_gauge(score: float, risk_level: str):
    """Renders a color-coded score gauge using matplotlib."""
    color_map = {"low": "#1D9E75", "medium": "#EF9F27", "high": "#E24B4A"}
    color = color_map.get(risk_level, "#888")

    fig, ax = plt.subplots(figsize=(5, 2.5), subplot_kw={"projection": "polar"})
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    # Background arc
    theta = np.linspace(np.pi, 0, 100)
    ax.fill_between(theta, 0.7, 1.0, color="#F0EFF8", alpha=0.8)

    # Score arc
    score_theta = np.linspace(np.pi, np.pi - (score / 100) * np.pi, 100)
    ax.fill_between(score_theta, 0.7, 1.0, color=color, alpha=0.9)

    ax.set_ylim(0, 1)
    ax.set_xlim(0, np.pi)
    ax.axis("off")
    ax.text(np.pi/2, 0.35, f"{score:.0f}", ha="center", va="center",
            fontsize=28, fontweight="bold", color=color)
    ax.text(np.pi/2, 0.1, f"{risk_level.upper()} RISK", ha="center", va="center",
            fontsize=10, color="#888888")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.pyplot(fig, use_container_width=True)
    plt.close()


def render_signal_cards(signals: list[dict]):
    """Renders detected signals as color-coded cards."""
    st.subheader("Signal Breakdown")
    color_map = {"red": "🔴", "orange": "🟡", "green": "🟢"}
    for signal in signals:
        icon = color_map.get(signal["flag"], "⚪")
        st.markdown(f"{icon} **{signal['signal']}** — `{signal['value']}`")


def render_profile_stats(profile: dict, features: dict):
    """Renders key profile metrics as metric cards."""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Followers", f"{profile.get('follower_count', 0):,}")
    col2.metric("Following", f"{profile.get('following_count', 0):,}")
    col3.metric("Engagement Rate", f"{features.get('engagement_rate', 0):.2f}%")
    col4.metric("Ghost Followers Est.", f"{features.get('ghost_follower_estimate', 0)*100:.0f}%")
