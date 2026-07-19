# Apply two replacements to local.bundle.js
# 1. Change "made by KODEK special for AntiDaunLeak" -> "desigined by SVITIK special for AntiSk3dLeak and CabbitGuard"
# 2. Change support section -> direct @SemenRecodesup link

path = r'C:\Users\tyert\OneDrive\Desktop\railway\static\assets\local.bundle.js'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replacement 1: Footer credit text
old1 = '"made by"," ",i.jsx("a",{className:"footer__credit-link",href:"https://t.me/uaown",target:"_blank",rel:"noreferrer",children:"KODEK"})," ","special for"," ",i.jsx("a",{className:"footer__credit-link",href:"https://t.me/antidaunleak",target:"_blank",rel:"noreferrer",children:"AntiDaunLeak"})'
new1 = '"desigined by SVITIK special for AntiSk3dLeak and CabbitGuard"'
content = content.replace(old1, new1, 1)
print(f'Replacement 1 done. Made by -> designed by')

# Replacement 2: Support section to direct link
old2_start = content.find('i.jsxs("div",{className:"footer__support"')
if old2_start >= 0:
    # Find the end of this structure
    end_marker = ']})]})'
    old2_end = content.find(end_marker, old2_start) + len(end_marker)
    old2 = content[old2_start:old2_end]
    new2 = 'i.jsx("a",{className:"footer__link",href:"https://t.me/SemenRecodesup",target:"_blank",rel:"noreferrer",children:"@SemenRecodesup"})'
    content = content.replace(old2, new2, 1)
    print(f'Replacement 2 done. Support section -> @SemenRecodesup')
else:
    print(f'Replacement 2: footer__support not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Final length: {len(content)}')
