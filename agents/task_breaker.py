# agents/task_breaker.py
"""
Task Breaker Agent
- Analyzes the user's raw input and splits it into independent subtasks (if any).
- Primary method: use OpenAI LLM to parse and return a JSON array of tasks.
- Fallback: simple heuristic splitting (by sentences / 'and' / semicolons).
Each task returned is a dict: {"id": "t1", "text": "..."}

Requires:
- OPENAI_API_KEY in environment (.env)
- config.yaml or config module to define default model (optional)
"""

import os
import json
import re
import uuid
from typing import List, Dict
from dotenv import load_dotenv
import openai
from loguru import logger

# Load environment
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in environment (.env)")

openai.api_key = OPENAI_API_KEY

# Default model — change to the model you have access to
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class TaskBreaker:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    def _clean_llm_output(self, text: str) -> str:
        """Remove markdown fences and leading/trailing noise."""
        text = text.strip()
        # remove fenced code blocks
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return text

    def break_into_tasks(self, user_prompt: str) -> List[Dict]:
        """
        Return a list of tasks derived from user_prompt.
        Each task is a dict with 'id' and 'text'.
        """
        system_prompt = (
            "You are a utility that breaks a user's single input into independent, "
            "numbered subtasks. If the user's input includes multiple requests or "
            "questions, split them. If it's a single request, return a single task. "
            "Return ONLY valid JSON: an array of objects with keys 'id' and 'text'. "
            "Keep task texts short (<= 120 chars). Example: [{\"id\":\"t1\",\"text\":\"Find top RN libraries 2025\"}]."
        )
        user_prompt_wrapped = (
            f"User input: '''{user_prompt}'''\n\n"
            "Return a JSON array as described above."
        )

        try:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt_wrapped}
                ],
                temperature=0.0,
                max_tokens=512,
            )
            raw = resp["choices"][0]["message"]["content"]
            cleaned = self._clean_llm_output(raw)
            tasks = json.loads(cleaned)

            # normalize tasks and ensure ids
            out = []
            for i, t in enumerate(tasks, start=1):
                tid = t.get("id") or f"t{i}"
                text = (t.get("text") or "").strip()
                if not text:
                    continue
                out.append({"id": str(tid), "text": text})
            if not out:
                raise ValueError("LLM returned no valid tasks")
            return out

        except Exception as e:
            logger.warning(f"TaskBreaker LLM path failed: {e}. Falling back to heuristics.")
            return self._heuristic_split(user_prompt)

    def _heuristic_split(self, user_prompt: str) -> List[Dict]:
        """
        Very simple fallback splitting:
        - Split by newline, semicolon, ' and ' (lowercase), or question marks.
        - Merge very short fragments.
        """
        text = user_prompt.strip()
        # prefer newlines first
        parts = re.split(r"\n+|;|\?|(?i)\sand\s", text)
        parts = [p.strip() for p in parts if p.strip()]

        # if it's still one part, try sentence tokenization by period
        if len(parts) == 1:
            parts = [p.strip() for p in re.split(r"\. ", text) if p.strip()]

        out = []
        for i, p in enumerate(parts, start=1):
            if len(p) < 15 and i < len(parts):
                # try to merge with next if fragment too short
                continue
            out.append({"id": f"t{i}", "text": p})
        # ensure at least one task
        if not out:
            out = [{"id": "t1", "text": text}]

        return out


# Quick test block (only run when executed directly)
if __name__ == "__main__":
    tb = TaskBreaker()
    sample = "Find top React Native libraries in 2025, list their pros/cons, and give usage examples. Also check GitHub activity."
    tasks = tb.break_into_tasks(sample)
    print(json.dumps(tasks, indent=2, ensure_ascii=False))
