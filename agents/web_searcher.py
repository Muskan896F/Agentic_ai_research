# agents/web_searcher.py
"""
Web Searcher Agent
- Takes a subtask (text) as input
- Queries the Serper API for relevant URLs
- Fetches & cleans page content using BeautifulSoup
- Returns structured results: [{"url":..., "title":..., "snippet":..., "text":...}]
"""

from typing import List, Dict
from tools.serper_api import serper_search
from tools.content_extractor import fetch_page_text
from dotenv import load_dotenv
import os
from loguru import logger

load_dotenv()
SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", 6))
MAX_PAGES_PER_TASK = int(os.getenv("MAX_PAGES_PER_TASK", 10))


class WebSearcher:
    def __init__(self, top_k: int = SEARCH_TOP_K, pages_per_task: int = MAX_PAGES_PER_TASK):
        self.top_k = top_k
        self.pages_per_task = pages_per_task

    def search_for_task(self, task_text: str) -> List[Dict]:
        """
        Run search for the given task and return list of page dicts.
        Each page dict: {"url": str, "title": str, "snippet": str, "text": str}
        """
        logger.info(f"🔎 Searching for task: {task_text}")

        # Define 2–3 query variations
        queries = [
            task_text,
            f"{task_text} 2024 2025 overview",
            f"{task_text} site:github.com",
        ]

        results = []
        seen_urls = set()

        for q in queries:
            hits = serper_search(q, num_results=self.top_k)
            for h in hits:
                url = h.get("link")
                if not url or url in seen_urls:
                    continue

                seen_urls.add(url)
                title = h.get("title")
                snippet = h.get("snippet")
                text = fetch_page_text(url)

                results.append({
                    "url": url,
                    "title": title,
                    "snippet": snippet,
                    "text": text
                })

                if len(results) >= self.pages_per_task:
                    break
            if len(results) >= self.pages_per_task:
                break

        logger.info(f"✅ Found {len(results)} pages for task.")
        return results


# Quick test
if __name__ == "__main__":
    ws = WebSearcher()
    out = ws.search_for_task("Top React Native libraries 2025")
    for r in out[:2]:  # show first 2
        print(r["title"], r["url"])
