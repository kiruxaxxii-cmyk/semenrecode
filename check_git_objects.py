import os
import subprocess
from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")

print("Checking git objects...")
# Search git objects for "admin.header.subtitle" or "lucide-react" or "vt="
git_dir = ROOT_DIR / ".git"
if git_dir.exists():
    print("Found .git directory!")
    # Find all object files
    objects = list((git_dir / "objects").rglob("*"))
    print("Git objects count:", len(objects))
    for obj in objects:
        if obj.is_file() and len(obj.name) == 38:
            try:
                # Read compressed git object
                import zlib
                content = zlib.decompress(obj.read_bytes()).decode("utf-8", errors="ignore")
                if "import{c as R,r as p,u as ts" in content and len(content) > 100000:
                    print(f"FOUND EXACT ORIGINAL 142KB JS IN GIT OBJECT {obj.name}! Length: {len(content)}")
                    # Find start of JS file
                    idx = content.find("import{c as R")
                    if idx != -1:
                        js_file = content[idx:]
                        (ROOT_DIR / "assets" / "AdminPage-zjEM4fPO.js").write_text(js_file, encoding="utf-8")
                        print("RESTORED EXACT 142KB ORIGINAL FILE TO assets/AdminPage-zjEM4fPO.js!")
                        exit(0)
            except Exception as e:
                pass
else:
    print(".git directory not found")
