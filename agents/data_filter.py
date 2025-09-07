"""
Data Filter Agent
- Input: subtask text + list of web page dicts
- Uses OpenAI LLM to extract relevant claims/info from each page
- Returns list of structured evidence:
  {"source_url":..., "title":..., "claim":..., "excerpt":..., "confidence":...}
"""

import os
import re
import json
from typing import List, Dict
from dotenv import load_dotenv
import openai
from loguru import logger

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in .env")

openai.api_key = OPENAI_API_KEY


class DataFilter:
    def __init__(self, model: str = MODEL_NAME):
        self.model = model

    def filter_relevant(self, task_text: str, pages: List[Dict]) -> List[Dict]:
        """
        For each page, ask LLM to pull relevant claims about the task.
        Returns a sorted list of evidence (high → low confidence).
        """
        evidence = []

        for p in pages:
            text = p.get("text")
            if not text:
                continue

            prompt = (
                f"Task: {task_text}\n\n"
                f"Page Title: {p.get('title')}\nURL: {p.get('url')}\n\n"
                f"Content:\n'''{text[:5000]}'''\n\n"
                "Extract only the information relevant to the task. "
                "Return a JSON array where each item has: "
                "claim (short sentence), excerpt (max 200 chars), confidence (0-1). "
                "If nothing is relevant, return []."
            )

            try:
                resp = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an extractor. Output JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    max_tokens=500,
                )
                raw = resp["choices"][0]["message"]["content"]
                raw = re.sub(r"^```(?:json)?", "", raw)
                raw = re.sub(r"```$", "", raw)
                items = json.loads(raw)

                for it in items:
                    evidence.append({
                        "source_url": p.get("url"),
                        "title": p.get("title"),
                        "claim": it.get("claim"),
                        "excerpt": it.get("excerpt"),
                        "confidence": float(it.get("confidence", 0))
                    })

            except Exception as e:
                logger.warning(f"⚠️ Extraction failed for {p.get('url')}: {e}")
                # fallback: use snippet as low-confidence claim
                if p.get("snippet"):
                    evidence.append({
                        "source_url": p.get("url"),
                        "title": p.get("title"),
                        "claim": p.get("snippet")[:200],
                        "excerpt": p.get("snippet")[:200],
                        "confidence": 0.3
                    })

        # sort by confidence
        evidence_sorted = sorted(evidence, key=lambda x: x["confidence"], reverse=True)
        return evidence_sorted

    # 🔹 Wrapper method for unit tests
    def filter(self, docs: List[Dict]) -> List[Dict]:
        """
        Simple filter for unit tests:
        - Removes entries with missing/empty 'content'
        """
        if not docs:
            return []
        return [doc for doc in docs if doc.get("content")]


# Quick test
if __name__ == "__main__":
    df = DataFilter()
    fake_pages = [
        {"url": "https://example.com", "title": "React Native 2025", "text": "React Native 0.76 added new features and Expo SDK improved..."},
    ]
    out = df.filter_relevant("Top React Native libraries 2025", fake_pages)
    print(json.dumps(out, indent=2))
