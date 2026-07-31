import json
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
transcript_path = Path(r"C:\Users\tyert\.gemini\antigravity\brain\35462a15-c417-4e66-88a8-f2ca42cfef25\.system_generated\logs\transcript_full.jsonl")

with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f):
        if "AdminPage-zjEM4fPO.js" in line and ("import{c as R,r as p" in line or "export{vt as AdminPage" in line):
            print(f"Line {i} matches!")
            data = json.loads(line)
            content = str(data)
            # Find import{c as R ... export{vt as AdminPage,vt as default};
            idx1 = content.find('import{c as R,r as p')
            if idx1 == -1:
                idx1 = content.find('import { c as R, r as p')
            if idx1 != -1:
                idx2 = content.find('export{vt as AdminPage', idx1)
                if idx2 != -1:
                    idx3 = content.find('};', idx2)
                    js_code = content[idx1:idx3+2]
                    # Unescape string
                    js_code = js_code.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                    print(f"FOUND ORIGINAL CODE IN LINE {i}! Length: {len(js_code)}")
                    out_file = ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js"
                    out_file.write_text(js_code, encoding="utf-8")
                    print("EXACT ORIGINAL AdminPage-zjEM4fPO.js RESTORED SUCCESSFULLY!")
                    exit(0)
