# orchestrator.py
"""
Orchestrator
- Central controller that runs the pipeline:
  1. Break tasks
  2. Search web
  3. Filter relevant info
  4. Summarize findings
  5. Write final report
"""

from agents.task_breaker import TaskBreaker
from agents.web_searcher import WebSearcher
from agents.data_filter import DataFilter
from agents.summarizer import Summarizer
from agents.report_writer import ReportWriter
from memory.short_term import ShortTermMemory
from loguru import logger
from typing import List, Dict


class Orchestrator:
    def __init__(self):
        self.task_breaker = TaskBreaker()
        self.web_searcher = WebSearcher()
        self.data_filter = DataFilter()
        self.summarizer = Summarizer()
        self.report_writer = ReportWriter()
        self.memory = ShortTermMemory()

    def run(self, topic: str) -> str:
        logger.info(f"🚀 Starting research on: {topic}")

        # Step 1: Break into tasks
        tasks = self.task_breaker.break_into_tasks(topic)
        for t in tasks:
            self.memory.add_task(t["id"], t["text"])

        task_summaries: List[Dict] = []

        # Step 2–4: Process each task
        for task in self.memory.get_tasks():
            task_id, task_text = task["id"], task["text"]
            logger.info(f"📝 Processing task {task_id}: {task_text}")

            # Web search
            pages = self.web_searcher.search_for_task(task_text)

            # Data filtering
            evidence = self.data_filter.filter_relevant(task_text, pages)
            for ev in evidence:
                self.memory.add_evidence(task_id, ev)

            # Summarization
            summary = self.summarizer.summarize_task(task_text, evidence)
            task_summaries.append(summary)

            # Mark done
            self.memory.set_task_done(task_id)

        # Step 5: Write final report
        markdown_text = self.report_writer.build_markdown(topic, task_summaries)
        md_file = self.report_writer.save_markdown(topic, markdown_text)
        self.report_writer.save_html(md_file)
        self.report_writer.save_pdf(md_file)

        logger.info(f"✅ Research complete. Report saved: {md_file}")
        return md_file
