# tools/serper_api.py
"""
Serper API Wrapper
- Sends a search query to Serper.dev (Google Search API)
- Returns simplified results: [{"title":..., "link":..., "snippet":...}, ...]
"""

import os
import requests
from dotenv import load_dotenv
from typing import List, Dict
from loguru import logger

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not SERPER_API_KEY:
    raise ValueError("Missing SERPER_API_KEY in .env")

SEARCH_URL = "https://google.serper.dev/search"


def serper_search(query: str, num_results: int = 6) -> List[Dict]:
    """
    Run a Serper search query.
    """
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": num_results}

    try:
        resp = requests.post(SEARCH_URL, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("organic", [])[:num_results]:
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
            })

        return results

    except Exception as e:
        logger.error(f"⚠️ Serper search failed for query '{query}': {e}")
        return []


# Quick test
if __name__ == "__main__":
    out = serper_search("Top React Native libraries 2025", num_results=3)
    for r in out:
        print(r["title"], "->", r["link"])
