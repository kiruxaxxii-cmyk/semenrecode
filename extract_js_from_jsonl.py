import json
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
transcript_path = Path(r"C:\Users\tyert\.gemini\antigravity\brain\35462a15-c417-4e66-88a8-f2ca42cfef25\.system_generated\logs\transcript_full.jsonl")

with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        if "AdminPage-zjEM4fPO.js" in line and ("TargetContent" in line or "CodeContent" in line or "content" in line):
            try:
                data = json.loads(line)
                # Search inside tool_calls or content
                tool_calls = data.get("tool_calls", [])
                for tc in tool_calls:
                    args = tc.get("args", {})
                    for key in ["TargetContent", "CodeContent", "ReplacementContent"]:
                        val = args.get(key, "")
                        if "import{" in val or "import {" in val:
                            if len(val) > 10000:
                                print(f"Found match in line {i}, key {key}, len {len(val)}")
                                out_file = ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js"
                                out_file.write_text(val, encoding="utf-8")
                                print("RESTORED ORIGINAL AdminPage-zjEM4fPO.js SUCCESSFULLY!")
                                exit(0)
            except Exception as e:
                pass
