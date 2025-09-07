# reports/export_pdf.py
"""
Utility script to convert a Markdown report into a PDF.
"""

from pathlib import Path
import markdown2
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet


def markdown_to_pdf(md_file: str, pdf_file: str = None) -> str:
    """
    Convert a Markdown file into a PDF.
    """
    md_path = Path(md_file)
    if not md_path.exists():
        raise FileNotFoundError(f"❌ Markdown file not found: {md_file}")

    # read markdown and convert to HTML-like
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    html_text = markdown2.markdown(md_text)

    # set PDF path
    pdf_file = pdf_file or str(md_path).replace(".md", ".pdf")

    # prepare PDF
    doc = SimpleDocTemplate(pdf_file, pagesize=LETTER)
    styles = getSampleStyleSheet()
    flowables = []

    for line in html_text.splitlines():
        if line.strip():
            flowables.append(Paragraph(line, styles["Normal"]))
            flowables.append(Spacer(1, 12))

    doc.build(flowables)
    return pdf_file


# Quick test
if __name__ == "__main__":
    # since you run this from inside "reports/", just use relative file
    md = "sample_topic.md"
    pdf = markdown_to_pdf(md)
    print(f"✅ PDF generated: {pdf}")
