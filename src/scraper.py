import os
from apify_client import ApifyClient
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))


def fetch_competitor_posts(company_urls, limit=10):
    actor_id = "supreme_coder/linkedin-post"

    run_input = {
        "urls": company_urls,
        "limitPerSource": limit,
        "scrapeAdditionalInfo": True,
        "getRawData": False
    }

    print(f"🚀 Starting Supreme Scraper for {len(company_urls)} companies...")

    try:
        run = client.actor(actor_id).call(run_input=run_input)
        processed_posts = []

        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            # MAPPING KEYS FROM YOUR JSON:
            processed_posts.append({
                'company': item.get('authorName', 'Unknown'),
                'text': item.get('text', ''),
                'likes': item.get('numLikes', 0),
                'comments': item.get('numComments', 0),
                'shares': item.get('numShares', 0),
                'post_url': item.get('url', ''),
                # e.g., linkedinVideo, image, article
                'format_type': item.get('type', 'text'),
                'timestamp': item.get('postedAtISO', '')
            })

        return pd.DataFrame(processed_posts)

    except Exception as e:
        print(f"❌ Apify Error: {e}")
        return pd.DataFrame()
