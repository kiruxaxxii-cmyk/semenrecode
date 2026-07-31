import json
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
transcript_path = Path(r"C:\Users\tyert\.gemini\antigravity\brain\35462a15-c417-4e66-88a8-f2ca42cfef25\.system_generated\logs\transcript_full.jsonl")

with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        if i == 970:
            print("Found line 970!")
            data = json.loads(line)
            for tc in data.get("tool_calls", []):
                args = tc.get("args", {})
                for k, v in args.items():
                    print(f"Arg {k}:")
                    print(str(v)[:500])
