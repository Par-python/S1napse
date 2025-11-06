# telemetry/storage.py
import gzip
import json

class SessionWriter:
    def __init__(self, path):
        self.path = path
        self.f = gzip.open(self.path, "at", encoding="utf-8")  # append text mode
        # write a small header line (optional)
        # self.f.write(json.dumps({"meta":"session start"}) + "\n")

    def write(self, obj: dict):
        # ensure serializable
        self.f.write(json.dumps(obj, default=str) + "\n")
        # flush occasionally
        self.f.flush()

    def close(self):
        try:
            self.f.close()
        except Exception:
            pass
