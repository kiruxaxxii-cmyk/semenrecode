import json
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
transcript_path = Path(r"C:\Users\tyert\.gemini\antigravity\brain\35462a15-c417-4e66-88a8-f2ca42cfef25\.system_generated\logs\transcript_full.jsonl")

with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        if "AdminPage-zjEM4fPO.js" in line and ("lucide-react" in line or "export{vt as AdminPage" in line):
            print(f"Line {i} matching...")
            idx = line.find("import{c as R")
            if idx != -1:
                # Find end of code
                end_idx = line.find("export{vt as AdminPage", idx)
                if end_idx != -1:
                    code_end = line.find("}", end_idx)
                    full_code = line[idx:code_end+1]
                    print(f"FOUND FULL ORIGINAL CODE IN LINE {i}! Len: {len(full_code)}")
                    out_file = ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js"
                    out_file.write_text(full_code, encoding="utf-8")
                    print("FULLY RESTORED EXACT ORIGINAL AdminPage-zjEM4fPO.js!")
                    exit(0)
