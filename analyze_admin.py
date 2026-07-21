import re
from pathlib import Path

s = (Path(__file__).parent / "assets" / "index-BgNmguIY.js").read_text(encoding="utf-8", errors="ignore")

for kw in ["admin", "check(", "isAdmin", "u&&", "media"]:
    print(f"\n=== searching {kw} ===")
    count = 0
    idx = 0
    while count < 8:
        i = s.find(kw, idx)
        if i == -1:
            break
        ctx = s[max(0, i-60):i+120]
        if any(x in ctx for x in ["admin", "Admin", "media", "check"]):
            print(ctx.replace("\n", " "))
            count += 1
        idx = i + len(kw)
