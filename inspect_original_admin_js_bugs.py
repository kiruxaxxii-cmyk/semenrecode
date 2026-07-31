from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
admin_file = ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js"

content = admin_file.read_text(encoding="utf-8", errors="ignore")
print("Original file size:", len(content))
print("First 300 chars:")
print(content[:300])

print("\nLast 300 chars:")
print(content[-300:])
