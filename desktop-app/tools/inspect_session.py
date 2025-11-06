# tools/inspect_session.py
import gzip
import json
import sys
from pathlib import Path

# Use provided argument, or fall back to the latest session file
if len(sys.argv) > 1:
    path = Path(sys.argv[1])
else:
    sessions_dir = Path(__file__).resolve().parent.parent / "sessions"
    latest = sorted(sessions_dir.glob("session_*.jsonl.gz"))[-1]
    path = latest

count = 0
first = None
last = None

with gzip.open(path, "rt", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        count += 1
        if first is None:
            first = obj
        last = obj

print(f"Analyzing session: {path.name}")
print("Samples:", count)
print("\nFirst sample:")
print(json.dumps(first, indent=2))
print("\nLast sample:")
print(json.dumps(last, indent=2))
