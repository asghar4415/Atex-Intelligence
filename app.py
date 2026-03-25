import streamlit as st
import pandas as pd
import plotly.express as px
import os
from src.scraper import fetch_linkedin_posts
from src.analyzer import categorize_post, generate_strategic_comparison

# Setup
ATEX_URL = "https://www.linkedin.com/company/atex/"
COMPETITORS = {
    "Stibo DX": "https://www.linkedin.com/company/stibodx/",
    "Naviga": "https://www.linkedin.com/company/nvgt/",
    "WoodWing": "https://www.linkedin.com/company/woodwing/",
    "Arc XP": "https://www.linkedin.com/company/arc-xp/"
}

st.set_page_config(page_title="Atex Command Center", layout="wide")

# --- DATA LOADING HELPERS ---


def process_with_ai(df):
    results = []
    for _, row in df.iterrows():
        cat = categorize_post(row['text'], row['format_type'])
        results.append(cat)
    return pd.concat([df, pd.DataFrame(results)], axis=1)


# --- SIDEBAR ---
st.sidebar.title("🏹 Intel Controls")
if not os.path.exists('data/atex_data.csv'):
    st.sidebar.warning("⚠️ No Atex context found. Run Atex Sync first.")

if st.sidebar.button("🔄 Sync Atex (Own Data)"):
    with st.spinner("Scraping Atex for context..."):
        df_atex = fetch_linkedin_posts([ATEX_URL], limit=10)
        df_atex = process_with_ai(df_atex)
        if not os.path.exists('data'):
            os.makedirs('data')
        df_atex.to_csv('data/atex_data.csv', index=False)
        st.sidebar.success("Atex Context Updated!")

selected_comps = st.sidebar.multiselect(
    "Target Competitors", list(COMPETITORS.keys()))
scrape_limit = st.sidebar.slider("Post Depth", 5, 30, 10)

if st.sidebar.button("🚀 Run Competitive Audit"):
    if not selected_comps:
        st.error("Select competitors first!")
    else:
        with st.spinner("Intercepting competitor signals..."):
            urls = [COMPETITORS[c] for c in selected_comps]
            df_comp = fetch_linkedin_posts(urls, limit=scrape_limit)
            df_comp = process_with_ai(df_comp)
            df_comp.to_csv('data/analyzed_posts.csv', index=False)
            st.rerun()

# --- MAIN DASHBOARD ---
st.title("🏹 Atex Strategic Market Intelligence")

if os.path.exists('data/atex_data.csv') and os.path.exists('data/analyzed_posts.csv'):
    df_atex = pd.read_csv('data/atex_data.csv')
    df_comp = pd.read_csv('data/analyzed_posts.csv')

    t1, t2, t3 = st.tabs(
        ["📊 Market Battlefield", "🧠 Executive Deep Dive", "🎯 Future Action Plan"])

    with t1:
        st.subheader("Engagement Benchmarking")
        # Combine data for visualization
        combined_df = pd.concat([df_atex, df_comp])
        fig = px.box(combined_df, x="company", y="likes",
                     color="company", title="Engagement Spread (Likes)")
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig2 = px.pie(combined_df, names="category",
                          title="Market Content Mix")
            st.plotly_chart(fig2)
        with col2:
            st.write("### Raw Intelligence Feed")
            st.dataframe(
                combined_df[['company', 'likes', 'category', 'text']].head(10))

    with t2:
        st.header("Competitive Intelligence Reports")
        target = st.selectbox("Select Competitor to Analyze",
                              selected_comps if selected_comps else df_comp['company'].unique())

        if st.button(f"Generate Atex vs {target} Report"):
            comp_slice = df_comp[df_comp['company'].str.contains(
                target.split()[0])]
            report = generate_strategic_comparison(df_atex, comp_slice, target)
            st.markdown(report)

    with t3:
        st.header("🚀 The 30-Day Atex Action Plan")
        st.info(
            "AI-generated roadmap based on the delta between Atex and the total market.")

        if st.button("Generate Master Strategy"):
            full_market_text = " ".join(df_comp['text'].astype(str).tolist())
            atex_text = " ".join(df_atex['text'].astype(str).tolist())

            prompt = f"Compare our strategy: {atex_text[:1000]} against market trends: {full_market_text[:2000]}. Give me 5 specific LinkedIn content series ideas that will win."
            # Call Gemini directly for this big summary
            from src.analyzer import client as genai_client
            resp = genai_client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt)
            st.success("Strategy Ready:")
            st.write(resp.text)

else:
    st.info("👋 Welcome. Please use the sidebar to 'Sync Atex' first, then run a 'Competitive Audit'.")
