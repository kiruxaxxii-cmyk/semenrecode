import json
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
transcript_path = Path(r"C:\Users\tyert\.gemini\antigravity\brain\35462a15-c417-4e66-88a8-f2ca42cfef25\.system_generated\logs\transcript_full.jsonl")

lines_to_check = [671, 675, 679, 974, 1008]

with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        if i in lines_to_check:
            print(f"=== LINE {i} ===")
            data = json.loads(line)
            # Print content or tool calls summary
            content = data.get("content", "")
            if content:
                print("Content sample:", content[:300])
            for tc in data.get("tool_calls", []):
                print("Tool call:", tc.get("name"))
                args = tc.get("args", {})
                for k, v in args.items():
                    if isinstance(v, str) and len(v) > 500:
                        print(f"Arg {k} len {len(v)}, sample:", v[:200])
                        if "import{c as R" in v or "vt=" in v:
                            print(f"FOUND ORIGINAL JS IN LINE {i} ARG {k}!")
                            out_file = ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js"
                            out_file.write_text(v, encoding="utf-8")
                            print("RESTORED ORIGINAL AdminPage-zjEM4fPO.js SUCCESSFULLY!")
                            exit(0)
