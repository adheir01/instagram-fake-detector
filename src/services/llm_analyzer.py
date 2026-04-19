import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()


def generate_summary(username, profile, features, result) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return "AI summary unavailable — add your GEMINI_API_KEY to .env to enable this."

    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-2.5-flash")  # updated from gemini-1.5-flash

    signals = "\n".join(f"- {s['signal']}: {s['value']}" for s in result.top_signals)

    prompt = f"""You are an influencer marketing analyst. A brand is considering sponsoring @{username}.

Profile data:
- Followers: {profile.get('follower_count', 0):,}
- Following: {profile.get('following_count', 0):,}
- Posts: {profile.get('post_count', 0)}
- Verified: {profile.get('is_verified', False)}

Key signals:
{signals}

Fake Score: {result.fake_score}/100
Risk level: {result.risk_level.upper()}

Write a 3-sentence sponsor recommendation. Be direct and practical.
State the risk level, explain the most important signal, and give a clear
recommendation (proceed / proceed with caution / avoid). No bullet points."""

    response = model.generate_content(prompt)
    return response.text