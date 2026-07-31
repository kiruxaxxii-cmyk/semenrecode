import re
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")

with open(ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js", "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

idx = js.find('admin-catalog-layout')
while idx != -1:
    print("admin-catalog-layout match:")
    print(js[max(0, idx-100):min(len(js), idx+300)])
    print("="*40)
    idx = js.find('admin-catalog-layout', idx+1)
