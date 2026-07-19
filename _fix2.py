path = r'C:\Users\tyert\OneDrive\Desktop\railway\static\assets\local.bundle.js'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace remaining made by in loader-credit (hidden)
old2 = '"made by"," ",i.jsx("a",{className:"loader-credit-link",href:"https://t.me/uaown",target:"_blank",rel:"noreferrer",children:"KODEK"})'
new2 = '"SemenRecode v4.21"'
content = content.replace(old2, new2, 1)
print('made by remaining:', content.find('made by'))

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done. Length:', len(content))
