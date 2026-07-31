import re

with open('assets/index-BKmpLbls.js', 'r', encoding='utf-8') as f:
    content = f.read()

for m in re.finditer(r'wy\s*=\s*[\'\"].{0,30}[\'\"]', content):
    print('Found wy=', repr(m.group(0)))

for m in re.finditer(r'[\w\$]+\(\"\/public\/bootstrap\"\)', content):
    print('Bootstrap fetch:', repr(content[max(0, m.start()-100):min(len(content), m.end()+100)]))

print("Total length:", len(content))
