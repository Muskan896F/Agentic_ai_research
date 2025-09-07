# agents/report_writer.py
"""
Report Writer Agent
- Compiles all task summaries into a final structured report.
- Outputs Markdown, HTML, and PDF.
"""

from typing import List, Dict, Optional
from pathlib import Path
import markdown2
import datetime
from loguru import logger
import os

# PDF converter
from reports.export_pdf import markdown_to_pdf

class ReportWriter:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📂 Reports will be saved in: {self.output_dir.resolve()}")

    def build_markdown(
        self,
        topic: str,
        task_summaries: List[Dict],
        include_appendix: bool = True
    ) -> str:
        """
        Build a Markdown report from task summaries.
        """
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        md = [f"# Research Report: {topic}\n", f"_Generated: {timestamp}_\n"]

        # Executive summary
        md.append("## Executive Summary\n")
        for t in task_summaries:
            md.append(f"- {t.get('summary', '')}\n")

        # Findings
        md.append("\n## Findings by Subtask\n")
        for i, t in enumerate(task_summaries, start=1):
            md.append(f"### {i}. {t.get('task', 'Unnamed Task')}\n")
            md.append(f"**Summary:** {t.get('summary', '')}\n")

            top_claims = t.get("top_claims", [])
            if top_claims:
                md.append("**Top Claims:**\n")
                for c in top_claims:
                    claim = c.get("claim") if isinstance(c, dict) else str(c)
                    src = c.get("source") if isinstance(c, dict) else ""
                    md.append(f"- {claim}  \n  _source: {src}_\n")

            uncertainties = t.get("uncertainties", [])
            if uncertainties:
                md.append("**Uncertainties / To Verify:**\n")
                for u in uncertainties:
                    md.append(f"- {u}\n")

        # Appendix
        if include_appendix:
            md.append("\n## Appendix\n")
            md.append("- **Methodology:** Task decomposition → Web search → Filtering → Summarization → Report writing\n")
            md.append("- **Limitations:** Limited sources, possible LLM hallucinations, freshness of web data\n")

        return "\n".join(md)

    def save_markdown(self, topic: str, markdown_text: str) -> Path:
        safe_name = topic.lower().replace(" ", "_")[:60]
        filename = self.output_dir / f"{safe_name}.md"
        filename.write_text(markdown_text, encoding="utf-8")
        logger.success(f"✅ Markdown report saved to {filename}")
        return filename

    def save_html(self, markdown_file: Path) -> Path:
        md_content = markdown_file.read_text(encoding="utf-8")
        html = markdown2.markdown(md_content)
        html_file = markdown_file.with_suffix(".html")
        html_file.write_text(html, encoding="utf-8")
        logger.success(f"✅ HTML report saved to {html_file}")
        return html_file

    def save_pdf(self, markdown_file: Path) -> Optional[Path]:
        """
        Convert Markdown report into a PDF.
        Returns the Path if successful, else None.
        """
        try:
            pdf_file = markdown_to_pdf(markdown_file)
            logger.success(f"✅ PDF report saved to {pdf_file}")
            return pdf_file
        except Exception as e:
            logger.error(f"❌ Failed to generate PDF: {e}")
            return None


# Quick test
if __name__ == "__main__":
    writer = ReportWriter()
    fake_summary = [
        {
            "task": "Top React Native libraries 2025",
            "summary": "React Native ecosystem in 2025 is strong.",
            "top_claims": [{"claim": "React Native 0.76 released", "source": "https://github.com"}],
            "uncertainties": ["Expo SDK adoption rate"]
        }
    ]
    md = writer.build_markdown("React Native 2025", fake_summary)
    md_path = writer.save_markdown("React Native 2025", md)
    writer.save_html(md_path)
    writer.save_pdf(md_path)
