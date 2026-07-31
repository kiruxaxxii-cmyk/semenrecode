with open('assets/index-BKmpLbls.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"/client_preview.png"', '"/client_preview.png?v=2"')

with open('assets/index-BKmpLbls.js', 'w', encoding='utf-8') as f:
    f.write(content)
