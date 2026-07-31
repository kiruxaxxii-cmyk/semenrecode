with open('assets/index-BKmpLbls.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"/svg/Vector.svg"', '"/semenicon.png"')

with open('assets/index-BKmpLbls.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement complete.")
