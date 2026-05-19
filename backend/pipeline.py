import feedparser
import requests
from google import genai
import json
import os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def fetch_raw_news():
    articles = []
    
    print("Fetching from BBC RSS...")
    rss_url = "http://feeds.bbci.co.uk/news/rss.xml"
    feed = feedparser.parse(rss_url)
    # ULTRA-SAFE TEST: Just grabbing 2 articles
    for entry in feed.entries[:2]: 
        articles.append({"title": entry.title, "url": entry.link, "source": "BBC RSS"})
        
    print("Fetching from SpaceNews API...")
    try:
        # ULTRA-SAFE TEST: Just grabbing 2 articles
        api_url = "https://api.spaceflightnewsapi.net/v4/articles/?limit=2" 
        response = requests.get(api_url).json()
        for item in response.get("results", []):
            articles.append({"title": item["title"], "url": item["url"], "source": "SpaceNews API"})
    except Exception as e:
        print(f"SpaceNews API Fetch failed: {e}")
        
    return articles

def process_with_llm(articles):
    if not articles:
        print("No new articles to send to LLM.")
        return []
        
    print(f"Sending {len(articles)} articles to Gemini for processing...")
    
    prompt = f"""
    You are an expert news editor. Analyze the following list of news articles. 
    For each individual article:
    1. Generate a strict 2-line concise summary.
    2. Cluster it into a broader overarching topic category (e.g., 'World Politics', 'Space & Tech', 'Business', 'Entertainment').
    3. Determine its sentiment: 'Positive', 'Neutral', or 'Negative'.

    Return the result strictly as a valid JSON array of objects. Each object must have these exact keys: "title", "url", "source", "summary", "topic", "sentiment".
    Do not add any markdown formatting, backticks (```json), or extra text outside the raw JSON array.

    Articles to process:
    {json.dumps(articles)}
    """
    
    try:
        # Using the newest 2026 model!
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        clean_text = response.text.strip().strip("```json").strip("```").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"Failed to parse LLM JSON response: {e}")
        return []