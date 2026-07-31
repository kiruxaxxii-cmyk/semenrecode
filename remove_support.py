with open('assets/index-BKmpLbls.js', 'r', encoding='utf-8') as f:
    content = f.read()

target = ',{title:"Поддержка",links:[{name:"Discord",href:o,external:!0}]}'
replacement = ''

if target in content:
    content = content.replace(target, replacement)
    with open('assets/index-BKmpLbls.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success")
else:
    print("Target not found!")
