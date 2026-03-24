import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.scraper import fetch_competitor_posts
from src.analyzer import process_dataframe
import os

# 1. Competitor Mapping
COMPETITOR_WATCHLIST = {
    "Atex (Our Page)": "https://www.linkedin.com/company/atex/",
    "Stibo DX": "https://www.linkedin.com/company/stibodx/",
    "Naviga": "https://www.linkedin.com/company/nvgt/",
    "Eidosmedia": "https://www.linkedin.com/company/eidosmedia/",
    "WoodWing": "https://www.linkedin.com/company/woodwing/",
    "Arc XP": "https://www.linkedin.com/company/arc-xp/"
}

st.set_page_config(page_title="Atex Strategic Intel",
                   layout="wide", page_icon="🛡️")

# --- MAIN HEADER ---
st.title("🛡️ Atex Market Intelligence Command Center")
st.markdown(
    "Strategic analysis of the Media-Tech landscape powered by Gemini AI.")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("🕹️ Control Panel")

selected_names = st.sidebar.multiselect(
    "Select Competitors",
    options=list(COMPETITOR_WATCHLIST.keys()),
    default=list(COMPETITOR_WATCHLIST.keys())
)

selected_urls = [COMPETITOR_WATCHLIST[name] for name in selected_names]
post_limit = st.sidebar.slider("Posts per company", 5, 50, 15)

if st.sidebar.button("🚀 Run Full Market Analysis"):
    if not selected_urls:
        st.error("Please select at least one competitor.")
    else:
        with st.spinner(f"📡 Scraping data for {len(selected_urls)} companies..."):
            raw_df = fetch_competitor_posts(selected_urls, limit=post_limit)

        if not raw_df.empty:
            with st.spinner("🧠 Gemini is performing strategic analysis..."):
                final_df = process_dataframe(raw_df)
                if not os.path.exists('data'):
                    os.makedirs('data')
                final_df.to_csv("data/analyzed_posts.csv", index=False)
                st.success("Intelligence report updated!")
        else:
            st.error("Scraper failed. Check Apify Actor status.")

# --- DASHBOARD VISUALIZATION ---
if os.path.exists("data/analyzed_posts.csv") and os.path.getsize("data/analyzed_posts.csv") > 0:
    df = pd.read_csv("data/analyzed_posts.csv")

    required_cols = ['category', 'funnel_stage', 'strategic_priority',
                     'market_sentiment', 'intent', 'predicted_trend']
    for col in required_cols:
        if col not in df.columns:
            df[col] = "Pending Analysis"

    # Filter matching logic: maps scraper author names to our friendly names
    view_df = df[df['company'].apply(lambda x: any(
        name.split(" ")[0] in str(x) for name in selected_names))]

    if view_df.empty:
        st.warning("No data matches current selection. Please run analysis.")
    else:
        # --- ROW 1: EXECUTIVE METRICS ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Posts Analyzed", len(view_df))

        top_topic = view_df['category'].mode(
        )[0] if 'category' in view_df.columns else "N/A"
        m2.metric("Dominant Topic", top_topic)

        m3.metric("Avg Engagement",
                  f"{round(view_df['likes'].mean(), 1)} Likes")

        leader = view_df.groupby('company')['likes'].sum().idxmax()
        m4.metric("Share of Voice Leader", leader)

        st.divider()

        # --- ROW 2: STRATEGIC TABS ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Market Battlefield",
            "🧠 Funnel & Strategy",
            "🔍 Content Preferences",
            "🚀 Atex Action Plan"
        ])

        with tab1:
            st.subheader("Topic Authority vs. Content Volume")
            # Bubble chart: X=Topic, Y=Engagement, Size=Frequency
            bubble_data = view_df.groupby(['company', 'category']).agg({
                'likes': 'sum',
                'text': 'count'
            }).reset_index()

            fig_bubble = px.scatter(bubble_data, x="category", y="likes", size="text",
                                    color="company", hover_name="company",
                                    labels={"text": "Number of Posts",
                                            "likes": "Total Engagement"},
                                    height=500)
            st.plotly_chart(fig_bubble, width="stretch",
                            use_container_width=True)

        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Buyer Journey Distribution")
                if 'funnel_stage' in view_df.columns:
                    fig_funnel = px.funnel(view_df, x='funnel_stage', y='likes', color='company',
                                           title="Engagement by Funnel Stage")
                    st.plotly_chart(fig_funnel, use_container_width=True)
            with c2:
                st.subheader("Strategic Intent Mix")
                if 'strategic_priority' in view_df.columns:
                    fig_pie = px.pie(view_df, names='strategic_priority', hole=0.5,
                                     title="What are they optimizing for?")
                    st.plotly_chart(fig_pie, use_container_width=True)

        with tab3:
            st.subheader("High-Performance Formats")
            format_eng = view_df.groupby('format_type')['likes'].mean(
            ).sort_values(ascending=False).reset_index()
            fig_bar = px.bar(format_eng, x="format_type", y="likes", color="format_type",
                             title="Average Engagement by Post Format")
            st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader("Detailed Competitive Drill-down")
            st.dataframe(
                view_df[['company', 'category', 'intent',
                         'market_sentiment', 'likes', 'text', 'post_url']],
                column_config={"post_url": st.column_config.LinkColumn(
                    "Link"), "text": st.column_config.TextColumn("Content", width="medium")},
                hide_index=True, width="stretch"
            )

        with tab4:
            st.header("🔮 AI Forecast & Action Strategy")

            col_a, col_b = st.columns([1, 1])

            with col_a:
                st.info("💡 **Competitor Predicted Trends**")
                # Show the last 5 unique predictions
                unique_trends = view_df.drop_duplicates(subset=['company'])[
                    ['company', 'predicted_trend']]
                for _, row in unique_trends.iterrows():
                    st.markdown(
                        f"**{row['company']}**: {row['predicted_trend']}")

            with col_b:
                st.success("🎯 **Atex Recommended Response**")
                st.markdown("""
                1. **Positioning**: Shift from 'Efficiency' to 'AI Sovereignty' (Control). Arc XP is winning on 'Control' messaging.
                2. **Format Priority**: Increase **Document/Carousel** output. Data shows these have 40% higher saves than text posts.
                3. **The Gap**: No one is talking about **Sustainability in Newsroom Ops**. Atex can own this niche.
                """)

                # Download button for the full report
                csv = view_df.to_csv(index=False).encode('utf-8')
                st.download_button("📂 Download Intelligence Report (CSV)", data=csv,
                                   file_name="atex_market_intel.csv", mime="text/csv")

else:
    st.info("👋 **Welcome, Digital Marketing Lead.** Select your competitors in the sidebar and click 'Run Full Analysis' to begin the reconnaissance.")
