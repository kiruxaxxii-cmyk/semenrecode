from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")

with open(ROOT_DIR / "assets" / "AdminPage-CRCcAHII.css", "r", encoding="utf-8", errors="ignore") as f:
    css = f.read()

print("AdminPage CSS length:", len(css))
print("First 1000 chars of AdminPage CSS:")
print(css[:1000])
