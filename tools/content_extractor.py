# tools/content_extractor.py
"""
Content Extractor
- Downloads HTML pages
- Removes scripts, styles, ads
- Returns clean readable text (paragraphs, list items)
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional
from loguru import logger

HEADERS = {"User-Agent": "AgenticResearchBot/1.0 (+https://example.com)"}


def fetch_page_text(url: str, timeout: int = 12) -> Optional[str]:
    """
    Fetch a URL and return cleaned text (paragraphs).
    If extraction fails, return None.
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "lxml")

        # remove unnecessary tags
        for s in soup(["script", "style", "noscript", "header", "footer", "svg", "meta", "link"]):
            s.decompose()

        # prefer article content if available
        article = soup.find("article")
        text_nodes = []

        if article:
            for p in article.find_all(["p", "li"]):
                t = p.get_text(strip=True)
                if t:
                    text_nodes.append(t)
        else:
            for p in soup.find_all("p"):
                t = p.get_text(strip=True)
                if t:
                    text_nodes.append(t)

        cleaned = "\n\n".join(text_nodes).strip()
        return cleaned[:200000] if cleaned else None

    except Exception as e:
        logger.warning(f"⚠️ Failed to fetch {url}: {e}")
        return None


# Quick test
if __name__ == "__main__":
    url = "https://reactnative.dev/"
    text = fetch_page_text(url)
    print(text[:500] if text else "No content extracted")
