import json
import os

class MemoryManager:
    def __init__(self, storage_file: str = "memory.json"):
        self.storage_file = storage_file
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, "w") as f:
                json.dump({}, f)

    def _load(self):
        with open(self.storage_file, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=2)

    def store_memory(self, key: str, value: str):
        data = self._load()
        data[key] = value
        self._save(data)

    def recall_memory(self, key: str):
        data = self._load()
        return data.get(key)

    def search_memory(self, query: str):
        data = self._load()
        results = []
        for k, v in data.items():
            if query in v:
                results.append((k, v))
        return results
