import json
import re
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
transcript_path = Path(r"C:\Users\tyert\.gemini\antigravity\brain\35462a15-c417-4e66-88a8-f2ca42cfef25\.system_generated\logs\transcript_full.jsonl")

if transcript_path.exists():
    print("Found transcript_full.jsonl!")
    with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "AdminPage-zjEM4fPO.js" in line:
                if "import{" in line or "import {" in line or "vt=" in line:
                    # Search for large string matches of JS code
                    match = re.search(r'import\{[^}]+\}from"\./index-BKmpLbls\.js".*?export\{vt as AdminPage,vt as default\};', line)
                    if match:
                        code = match.group(0)
                        print("FOUND EXACT ORIGINAL ADMIN CODE! Length:", len(code))
                        out_file = ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js"
                        out_file.write_text(code, encoding="utf-8")
                        print("RESTORED EXACT ORIGINAL AdminPage-zjEM4fPO.js!")
                        break
else:
    print("transcript_full.jsonl not found")
