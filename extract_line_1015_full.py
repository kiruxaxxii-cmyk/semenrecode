import json
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
transcript_path = Path(r"C:\Users\tyert\.gemini\antigravity\brain\35462a15-c417-4e66-88a8-f2ca42cfef25\.system_generated\logs\transcript_full.jsonl")

with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        if i == 1015:
            print("Line 1015 len:", len(line))
            idx = line.find("import{c as R")
            print("import index:", idx)
            if idx != -1:
                sub = line[idx:]
                print("sub sample:", sub[:500])
                end_idx = sub.rfind("export{vt as AdminPage")
                print("export index:", end_idx)
                if end_idx != -1:
                    full_code = sub[:end_idx + 35]
                    print("Full code length:", len(full_code))
                    out_file = ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js"
                    out_file.write_text(full_code, encoding="utf-8")
                    print("SUCCESSFULLY RESTORED EXACT ORIGINAL JS FROM LINE 1015!")
