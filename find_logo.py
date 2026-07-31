import re
with open('assets/index-BKmpLbls.js', 'r', encoding='utf-8') as f:
    content = f.read()

for m in re.finditer(r'img[^>]*logo', content):
    print('Logo:', m.group())

for m in re.finditer(r'src[:=][\s]*[\"\'][^\"]*logo', content):
    print('Src logo:', m.group())
