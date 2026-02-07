import json
from pathlib import Path
from typing import List, Dict, Any


class PitchDeckRegistry:
    def __init__(self, registry_path="data/registry/pitch_decks.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.registry_path.exists():
            self._save([])

    def _load(self) -> List[Dict[str, Any]]:
        with open(self.registry_path, "r") as f:
            return json.load(f)

    def _save(self, data: List[Dict[str, Any]]):
        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def register(self, entry: Dict[str, Any]):
        data = self._load()
        data.append(entry)
        self._save(data)

    def list_all(self):
        return self._load()

    def get_unanalyzed(self):
        return [d for d in self._load() if not d.get("analyzed")]

    def mark_analyzed(self, deck_id: str):
        data = self._load()
        for d in data:
            if d["id"] == deck_id:
                d["analyzed"] = True
        self._save(data)
