# agents/summarizer.py
"""
Summarizer Agent
- Input: subtask text + evidence list
- Uses OpenAI LLM to produce a structured summary
- Output: dict with keys:
  {
    "task": "...",
    "summary": "...",
    "top_claims": [{"claim": "...", "source": "..."}],
    "uncertainties": [...]
  }
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


class Summarizer:
    def __init__(self, model: str = MODEL_NAME):
        self.model = model

    def summarize_task(self, task_text: str, evidence: List[Dict]) -> Dict:
        """
        Generate summary JSON for one task.
        """
        # prepare evidence snippets
        evidence_snippets = []
        for e in evidence[:8]:  # limit to 8 for brevity
            snippet = e.get("claim") or e.get("excerpt") or ""
            evidence_snippets.append(f"- {snippet} (source: {e.get('source_url')})")

        prompt = (
            f"Task: {task_text}\n\n"
            f"Evidence:\n{chr(10).join(evidence_snippets)}\n\n"
            "Summarize findings relevant to this task.\n"
            "Return a JSON object with keys:\n"
            "- summary: 2-3 sentences overview\n"
            "- top_claims: array of {claim, source}\n"
            "- uncertainties: list of weak or unverified points\n"
        )

        try:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert summarizer. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=400,
            )
            raw = resp["choices"][0]["message"]["content"]
            raw = re.sub(r"^```(?:json)?", "", raw)
            raw = re.sub(r"```$", "", raw)
            result = json.loads(raw)
            result["task"] = task_text
            return result

        except Exception as e:
            logger.warning(f"⚠️ Summarization failed: {e}")
            # fallback: create a simple summary
            top_claims = [
                {"claim": e.get("claim"), "source": e.get("source_url")}
                for e in (evidence[:5] or [])
            ]
            return {
                "task": task_text,
                "summary": "Could not generate detailed summary, returning top claims.",
                "top_claims": top_claims,
                "uncertainties": []
            }


# Quick test
if __name__ == "__main__":
    s = Summarizer()
    fake_evidence = [
        {"claim": "React Native 0.76 was released with new features", "source_url": "https://github.com"},
        {"claim": "Expo SDK gained better support in 2025", "source_url": "https://expo.dev"},
    ]
    out = s.summarize_task("Top React Native libraries 2025", fake_evidence)
    print(json.dumps(out, indent=2))
