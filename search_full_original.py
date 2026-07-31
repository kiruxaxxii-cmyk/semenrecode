import json
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
transcript_path = Path(r"C:\Users\tyert\.gemini\antigravity\brain\35462a15-c417-4e66-88a8-f2ca42cfef25\.system_generated\logs\transcript_full.jsonl")

with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        if "import{c as R" in line:
            idx1 = line.find("import{c as R")
            idx2 = line.find("export{vt as AdminPage", idx1)
            if idx2 != -1:
                idx3 = line.find("};", idx2)
                code = line[idx1:idx3+2]
                print(f"Line {i}: code length {len(code)}")
                if len(code) > 100000:
                    print(f"FOUND FULL ORIGINAL JS FILE AT LINE {i}!")
                    out_file = ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js"
                    out_file.write_text(code, encoding="utf-8")
                    print("EXACT ORIGINAL VITE BUNDLE RESTORED TO ASSETS!")
                    exit(0)
