import re
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")

with open(ROOT_DIR / "assets" / "index-BKmpLbls.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

idx = js.find('Yo=')
if idx != -1:
    print("Yo component context:")
    print(js[max(0, idx-50):min(len(js), idx+300)])
