import re
from pathlib import Path

s = (Path(__file__).parent / "assets" / "index-BgNmguIY.js").read_text(encoding="utf-8", errors="ignore")

# Find API client definition
for pat in [r'baseURL[^,]{0,80}', r'fetch\([^)]{0,120}', r'hostname[^;]{0,120}', r'location\.host[^;]{0,120}', r'domain[^;]{0,120}', r'allowed[^;]{0,120}', r'origin[^;]{0,120}']:
    matches = re.findall(pat, s, re.I)
    if matches:
        print(f"\n=== {pat} ===")
        for m in sorted(set(matches))[:20]:
            print(m[:200])

# routes with createBrowserRouter or Routes
for pat in [r'\{path:"[^"]+"', r'element:[^,]{0,60}', r'"/[a-zA-Z0-9_-]+"']:
    matches = re.findall(pat, s)
    if matches:
        print(f"\n=== {pat} ===")
        for m in sorted(set(matches))[:40]:
            print(m)

# chunk files
chunks = sorted(set(re.findall(r'assets/[A-Za-z0-9_-]+\.js', s)))
print("\n=== chunk refs ===")
for c in chunks: print(c)

# api endpoints
apis = sorted(set(re.findall(r'["\'](/api/[a-zA-Z0-9_/-]+)["\']', s)))
print("\n=== api endpoints ===")
for a in apis: print(a)

# also search for method names like login, register
for kw in ['login', 'register', 'admin', 'launcher', 'payment', 'key', 'license']:
    idx = 0
    found = []
    while True:
        i = s.lower().find(kw, idx)
        if i == -1: break
        found.append(s[max(0,i-30):i+60].replace('\n',' '))
        idx = i + len(kw)
        if len(found) >= 3: break
    if found:
        print(f"\n=== {kw} samples ===")
        for f in found: print(f)
