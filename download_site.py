import re
import os
import urllib.request
import urllib.parse
from pathlib import Path

BASE = "https://skycoreclient.xyz"
OUT = Path(__file__).resolve().parent

def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()

def save_rel(path: str, data: bytes):
    dest = OUT / path.lstrip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    print(f"saved {dest}")

def collect_paths(text: str) -> set[str]:
    patterns = [
        r'["\'](/assets/[^"\']+)["\']',
        r'url\((/assets/[^)]+)\)',
        r'["\'](/[^"\']+\.(?:png|jpg|jpeg|gif|webp|svg|ico|woff2?|ttf|mp4|webm))["\']',
    ]
    found = set()
    for p in patterns:
        for m in re.findall(p, text):
            found.add(m.split("?")[0])
    return found

def main():
    queue = {
        "/",
        "/index.html",
        "/favicon.ico",
        "/assets/index-BgNmguIY.js",
        "/assets/index-h4STkTJJ.css",
        "/files/launcher.exe",
    }
    done = set()

    while queue:
        rel = queue.pop()
        if rel in done:
            continue
        done.add(rel)

        url = BASE + rel if rel.startswith("/") else BASE + "/" + rel
        try:
            data = fetch(url)
        except Exception as e:
            print(f"skip {url}: {e}")
            continue

        local = rel if rel != "/" else "/index.html"
        save_rel(local, data)

        if local.endswith((".js", ".css", ".html")):
            text = data.decode("utf-8", errors="ignore")
            for p in collect_paths(text):
                queue.add(p)

            # chunk imports in js
            for m in re.findall(r'import\(["\'](\./[^"\']+)["\']\)', text):
                pass
            for m in re.findall(r'["\'](/[^"\']+)["\']', text):
                if any(m.endswith(ext) for ext in (".js", ".css", ".png", ".jpg", ".svg", ".webp", ".woff", ".woff2", ".ico", ".mp4")):
                    queue.add(m.split("?")[0])

    # print analysis
    js_path = OUT / "assets" / "index-BgNmguIY.js"
    if js_path.exists():
        s = js_path.read_text(encoding="utf-8", errors="ignore")
        print("\n=== API paths ===")
        for a in sorted(set(re.findall(r'["\'](/api[^"\']*)["\']', s))):
            print(a)
        print("\n=== routes ===")
        for p in sorted(set(re.findall(r'path:\s*["\']([^"\']+)["\']', s))):
            print(p)
        print("\n=== keywords ===")
        for kw in ["domain", "localhost", "hwid", "token", "origin", "skycore", "VITE_", "location.host", "window.location"]:
            if kw.lower() in s.lower():
                print(kw, "-> found")

if __name__ == "__main__":
    main()
    print("\nApplying local patches...")
    import subprocess
    import sys

    subprocess.run([sys.executable, str(OUT / "patch_site.py")], check=False)
