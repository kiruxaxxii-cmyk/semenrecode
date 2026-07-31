import re
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")

with open(ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

idx = js.find('vt=({')
idx_return = js.find('return ns?', idx)
print("vt main return statement:")
print(js[idx_return:idx_return+1200])
