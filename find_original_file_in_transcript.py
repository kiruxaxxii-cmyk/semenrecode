import json
import re
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
transcript_path = Path(r"C:\Users\tyert\.gemini\antigravity\brain\35462a15-c417-4e66-88a8-f2ca42cfef25\.system_generated\logs\transcript_full.jsonl")

matches = []

with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        if "AdminPage-zjEM4fPO.js" in line:
            if "import{c as R,r as p" in line or "vt=" in line or "useDelayedLoading" in line:
                matches.append((i, line))

print(f"Total matching lines in transcript: {len(matches)}")
for idx, line in matches:
    print(f"--- Line {idx} ---")
    try:
        data = json.loads(line)
        # Check tool calls
        for tc in data.get("tool_calls", []):
            args = tc.get("args", {})
            for k, v in args.items():
                if isinstance(v, str) and ("import{c as R" in v or "vt=" in v) and len(v) > 20000:
                    print(f"Found original code in line {idx}, arg {k}, len {len(v)}")
                    out_file = ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js"
                    out_file.write_text(v, encoding="utf-8")
                    print("SUCCESSFULLY RESTORED EXACT ORIGINAL AdminPage-zjEM4fPO.js!")
                    exit(0)
    except Exception as e:
        pass
