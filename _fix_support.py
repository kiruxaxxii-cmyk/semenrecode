import os

path = r'C:\Users\tyert\OneDrive\Desktop\railway\static\assets\local.bundle.js'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('footer__support-trigger')
start = content.rfind('i.jsxs("div"', 0, idx - 5)
end_marker = ']})]})'
end_idx = content.find(end_marker, idx) + len(end_marker)

old_text = content[start:end_idx]
new_text = 'i.jsx("a",{className:"footer__link",href:"https://t.me/SemenRecodesup",target:"_blank",rel:"noreferrer",children:"@SemenRecodesup"})'

new_content = content.replace(old_text, new_text, 1)
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print(f'Done. Length: {len(new_content)}')
print(f'Found at: {idx}')
