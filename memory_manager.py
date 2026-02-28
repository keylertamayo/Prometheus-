import json
import os
import base64
from typing import Optional

try:
    from cryptography.fernet import Fernet
except Exception:
    Fernet = None


class MemoryManager:
    def __init__(self, storage_file: str = "memory.json", encryption_key: Optional[bytes] = None):
        self.storage_file = storage_file
        self._fernet = None
        if encryption_key:
            if Fernet is None:
                raise RuntimeError("cryptography package required for encrypted memory")
            # encryption_key expected to be base64 urlsafe bytes
            self._fernet = Fernet(encryption_key)

        if not os.path.exists(self.storage_file):
            # create an empty store (encrypted or plain depending on key)
            if self._fernet:
                token = self._fernet.encrypt(json.dumps({}).encode())
                with open(self.storage_file, "wb") as f:
                    f.write(token)
            else:
                with open(self.storage_file, "w") as f:
                    json.dump({}, f)

    def _load(self):
        if not os.path.exists(self.storage_file):
            return {}
        if self._fernet:
            with open(self.storage_file, "rb") as f:
                token = f.read()
            if not token:
                return {}
            data = self._fernet.decrypt(token)
            return json.loads(data.decode())
        else:
            with open(self.storage_file, "r") as f:
                return json.load(f)

    def _save(self, data):
        if self._fernet:
            token = self._fernet.encrypt(json.dumps(data).encode())
            with open(self.storage_file, "wb") as f:
                f.write(token)
        else:
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
            try:
                if isinstance(v, str) and query in v:
                    results.append((k, v))
            except Exception:
                continue
        return results

    def recall_all(self):
        return self._load()

    def recall_all(self):
        """Return a copy of the entire memory dictionary."""
        return self._load()
