import json
import os


LEVEL_ORDER = ["training", "deep_sea", "mid_sea"]
BADGE_RANK = {"none": 0, "bronze": 1, "silver": 2, "gold": 3}


class SaveManager:
    def __init__(self, path="save.json"):
        self.path = path
        self.data = self._load()

    def _default_data(self):
        return {
            "unlocked_level": LEVEL_ORDER[0],
            "completed_levels": [],
            "best_badges": {},
            "settings": {
                "music": True,
                "sfx": True,
            },
        }

    def _load(self):
        if not os.path.exists(self.path):
            data = self._default_data()
            self._save(data)
            return data

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        except (OSError, json.JSONDecodeError):
            loaded = {}

        data = self._default_data()
        data.update({k: v for k, v in loaded.items() if k in data})
        if data["unlocked_level"] not in LEVEL_ORDER:
            data["unlocked_level"] = LEVEL_ORDER[0]
        return data

    def _save(self, data=None):
        if data is not None:
            self.data = data
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def is_unlocked(self, level_id):
        return LEVEL_ORDER.index(level_id) <= LEVEL_ORDER.index(self.data["unlocked_level"])

    def unlock_next_after(self, level_id):
        if level_id not in LEVEL_ORDER:
            return
        current_index = LEVEL_ORDER.index(self.data["unlocked_level"])
        level_index = LEVEL_ORDER.index(level_id)
        if level_index + 1 < len(LEVEL_ORDER) and level_index >= current_index:
            self.data["unlocked_level"] = LEVEL_ORDER[level_index + 1]
        if level_id not in self.data["completed_levels"]:
            self.data["completed_levels"].append(level_id)
        self._save()

    def record_result(self, level_id, badge):
        current = self.data["best_badges"].get(level_id, "none")
        if BADGE_RANK.get(badge, 0) >= BADGE_RANK.get(current, 0):
            self.data["best_badges"][level_id] = badge
            self._save()

    def toggle_setting(self, name):
        if name in self.data["settings"]:
            self.data["settings"][name] = not self.data["settings"][name]
            self._save()
