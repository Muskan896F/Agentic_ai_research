# main.py
"""
Entry point for Agentic AI Research pipeline.
"""

from orchestrator import Orchestrator   # ✅ updated import
from loguru import logger
from pathlib import Path
import json
import datetime
import sys
import yaml


def setup_logging():
    """Configure log file inside logs/ directory."""
    Path("logs").mkdir(exist_ok=True)
    log_file = f"logs/run_{datetime.date.today()}.log"
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add(log_file, rotation="1 MB", level="DEBUG")
    return log_file


def save_telemetry(report_file: str, tasks_count: int):
    """Save run metadata into logs/telemetry.json."""
    telemetry = {
        "report_file": report_file,
        "tasks_processed": tasks_count,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    with open("logs/telemetry.json", "w", encoding="utf-8") as f:
        json.dump(telemetry, f, indent=2)


def load_config():
    """Load config.yaml for thresholds and API setup."""
    if not Path("config.yaml").exists():
        logger.warning("⚠️ No config.yaml found, using defaults.")
        return {}
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    setup_logging()
    config = load_config()

    topic = "Top React Native libraries in 2025"
    logger.info(f"🚀 Starting Agentic Research on: {topic}")

    orch = Orchestrator()
    report_file = orch.run(topic)

    tasks_count = len(orch.memory.get_tasks())
    save_telemetry(report_file, tasks_count)

    logger.info("🎯 Pipeline finished successfully.")
