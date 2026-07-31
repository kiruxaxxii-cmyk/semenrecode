import re
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")

with open(ROOT_DIR / "assets" / "index-BKmpLbls.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

idx = js.find('path:"/admin"')
if idx != -1:
    print("/admin route definition in router:")
    print(js[max(0, idx-100):min(len(js), idx+300)])
