import os
import json
from google import genai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_content(post_text, format_type):
    if not post_text or len(str(post_text)) < 20:
        return {
            "category": "Short Update", "funnel_stage": "Awareness",
            "target_persona": "General", "pain_point": "Visibility",
            "strategic_priority": "Retention", "predicted_trend": "N/A"
        }

    prompt = f"""
    Act as a B2B SaaS Strategic Consultant for Atex (Newsroom Software). 
    Perform a competitive audit on this post (Format: {format_type}):
    "{post_text}"
    
    Return ONLY JSON with these keys:
    1. "category": (AI Monetization, Workflow Efficiency, Governance/ISO, Audience Engagement, Digital Transformation)
    2. "funnel_stage": (TOFU: Education, MOFU: Solution-Seeking, BOFU: Decision/Case Study)
    3. "target_persona": (CTO, Editor-in-Chief, Digital Revenue Officer, Compliance Officer)
    4. "pain_point": (What specific problem are they solving? e.g., AI bot scraping, version control, subscription churn)
    5. "strategic_priority": (Thought Leadership, Demand Gen, Brand Trust, Partner Ecosystem)
    6. "predicted_trend": (Where is this competitor moving next?)
    7. "atex_counter_move": (A 1-sentence recommendation for Atex to beat this specific post)
    """

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception:
        return {
            "category": "Other", "funnel_stage": "TOFU",
            "target_persona": "General", "pain_point": "Unknown",
            "strategic_priority": "General", "predicted_trend": "Unknown",
            "atex_counter_move": "Maintain standard posting"
        }


def process_dataframe(df):
    print("🧠 Gemini is analyzing posts based on Media-Tech categories...")

    # We pass both text and format_type to the analyzer
    analysis_results = [analyze_content(
        row['text'], row['format_type']) for _, row in df.iterrows()]

    analysis_df = pd.DataFrame(analysis_results)
    return pd.concat([df.reset_index(drop=True), analysis_df.reset_index(drop=True)], axis=1)
