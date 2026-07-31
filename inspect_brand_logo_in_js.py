from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
index_js = ROOT_DIR / "assets" / "index-BKmpLbls.js"

content = index_js.read_text(encoding="utf-8", errors="ignore")

idx = content.find("brand")
while idx != -1:
    print("brand match at:", idx)
    print(content[max(0, idx-60):min(len(content), idx+140)])
    print("-" * 30)
    idx = content.find("brand", idx+1)
