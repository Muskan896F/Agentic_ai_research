# memory/short_term.py
"""
Short-Term Memory
- Holds in-run data (temporary, not persisted).
- Stores tasks, evidence, and notes during execution.
"""

from typing import Dict, Any, List


class ShortTermMemory:
    def __init__(self):
        self.state: Dict[str, Any] = {
            "tasks": [],        # [{"id": "t1", "text": "...", "status": "pending"}]
            "evidence": {},     # task_id -> [evidence dicts]
            "notes": []         # freeform notes
        }

    # ----- Task management -----
    def add_task(self, task_id: str, task_text: str):
        self.state["tasks"].append({"id": task_id, "text": task_text, "status": "pending"})

    def set_task_done(self, task_id: str):
        for t in self.state["tasks"]:
            if t["id"] == task_id:
                t["status"] = "done"

    def get_tasks(self) -> List[Dict]:
        return self.state["tasks"]

    # ----- Evidence management -----
    def add_evidence(self, task_id: str, evidence: Dict):
        self.state["evidence"].setdefault(task_id, []).append(evidence)

    def get_evidence(self, task_id: str) -> List[Dict]:
        return self.state["evidence"].get(task_id, [])

    # ----- Notes -----
    def add_note(self, note: str):
        self.state["notes"].append(note)

    def get_notes(self) -> List[str]:
        return self.state["notes"]


# Quick test
if __name__ == "__main__":
    mem = ShortTermMemory()
    mem.add_task("t1", "Find top React Native libraries 2025")
    mem.add_evidence("t1", {"claim": "React Native 0.76 released", "source": "github.com"})
    mem.set_task_done("t1")

    print("Tasks:", mem.get_tasks())
    print("Evidence:", mem.get_evidence("t1"))
