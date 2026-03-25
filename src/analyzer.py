import os
import json
from google import genai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={'api_version': 'v1'}
)

MODEL_ID = "gemini-2.5-flash"

# Core context for the AI
ATEX_MISSION = """
Atex provides smart solutions for the media industry. 
We support news publishers and media outlets to develop sustainable business models 
through innovative newsroom software. Our goal is to help publishers address 
and scale for tomorrow's challenges.
"""


def categorize_post(text, format_type):
    """Categorizes posts specifically for the Media-Tech industry."""
    if not text or len(str(text)) < 10:
        return {"category": "Short Update", "funnel_stage": "Awareness"}

    prompt = f"""
    {ATEX_MISSION}
    Analyze this LinkedIn post from a competitor in the news-tech space: "{text[:500]}"
    Return JSON only: {{
        "category": "AI/Innovation|Monetization|Newsroom Workflow|Case Study|Company Culture", 
        "funnel_stage": "Awareness|Consideration|Decision"
    }}
    """
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except:
        return {"category": "General News", "funnel_stage": "Awareness"}


def generate_strategic_comparison(atex_df, comp_df, comp_name):
    """Detailed comparison using Atex internal data as the benchmark."""

    atex_top = atex_df.sort_values(by='likes', ascending=False).head(5)[
        'text'].tolist()
    comp_top = comp_df.sort_values(by='likes', ascending=False).head(5)[
        'text'].tolist()

    prompt = f"""
    System: You are the Head of Digital Marketing at Atex. 
    Mission: {ATEX_MISSION}

    Task: Compare our (Atex) performance against {comp_name}.

    OUR TOP RECENT POSTS:
    {atex_top}

    THEIR ({comp_name}) TOP RECENT POSTS:
    {comp_top}

    STRUCTURE THE REPORT FOR THE ATEX LEADERSHIP TEAM:
    1. **Narrative War**: What story are they telling that we aren't? (e.g., Are they pushing AI harder? Are they focusing on subscriptions?)
    2. **The Engagement Delta**: Based on the likes, what is the market craving from them that we should adopt?
    3. **Technical Vulnerability**: Based on their claims, where is Atex's software (CMS/Workflow) objectively more 'future-proof'?
    4. **3 specific 'Counter-Strike' Content Ideas**: Content we should post this week to neutralise their momentum.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_ID, contents=prompt)
        return response.text
    except Exception as e:
        return f"Error generating report: {e}"


def generate_master_roadmap(atex_df, all_comps_df):
    """The Final Future Plan tab logic."""
    market_trends = all_comps_df.groupby('category')['likes'].sum().to_dict()

    prompt = f"""
    As Atex Marketing Head, look at the entire market data summary: {market_trends}.
    Our current content output: {atex_df['text'].head(5).tolist()}.

    Provide a 30-day Action Plan to dominate the Media-Tech space on LinkedIn.
    Include:
    - Content Type Mix (e.g., 40% Case Studies, 30% AI Workflow tips)
    - A specific series idea (e.g., 'The Sustainable Publisher' series)
    - Key metrics to track that prove we are beating the competition.
    """
    try:
        response = client.models.generate_content(
            model=MODEL_ID, contents=prompt)
        return response.text
    except Exception as e:
        return f"Error generating roadmap: {e}"
