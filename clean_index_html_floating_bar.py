from pathlib import Path

ROOT_DIR = Path(r"c:\Users\tyert\OneDrive\Desktop\nuclear")
index_html = ROOT_DIR / "index.html"

content = index_html.read_text(encoding="utf-8", errors="ignore")

idx = content.find("<!-- Floating Admin Auto-Upload Control Panel -->")
if idx != -1:
    end_idx = content.find("</script>", idx)
    if end_idx != -1:
        content = content[:idx] + content[end_idx+9:]
        index_html.write_text(content, encoding="utf-8")
        print("[INDEX.HTML CLEANED] Removed duplicate floating Auto-Upload control panel script!")
