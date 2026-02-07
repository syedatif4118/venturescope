import json
from pathlib import Path
from typing import Dict, Any


class KnowledgeStore:
    def __init__(self, base_dir="data"):
        self.base_dir = Path(base_dir)

        self.structured_dir = self.base_dir / "structured"
        self.analysis_dir = self.base_dir / "analyses"
        self.memo_dir = self.base_dir / "memos"

        for d in [
            self.structured_dir,
            self.analysis_dir,
            self.memo_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    def save_structured(self, deck_id: str, data: Dict[str, Any]):
        path = self.structured_dir / f"{deck_id}.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def save_analysis(self, deck_id: str, analysis: Dict[str, Any]):
        path = self.analysis_dir / f"{deck_id}_analysis.json"
        with open(path, "w") as f:
            json.dump(analysis, f, indent=2)

    def save_memo(self, deck_id: str, memo: str):
        path = self.memo_dir / f"{deck_id}_memo.md"
        with open(path, "w") as f:
            f.write(memo)
