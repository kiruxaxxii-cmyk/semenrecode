with open('assets/index-BKmpLbls.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"/semenicon.png"', '"/semenicon.png?v=3"')

with open('assets/index-BKmpLbls.js', 'w', encoding='utf-8') as f:
    f.write(content)
