import re

with open('assets/index-BKmpLbls.js', 'r', encoding='utf-8') as f:
    content = f.read()

m = re.search(r'wy\s*=\s*([\'\"].*?[\'\"])', content)
if m:
    print('Found wy definition:', m.group(0))
    idx = m.start()
    print(repr(content[max(0, idx-100):min(len(content), idx+100)]))
else:
    print('wy not found')
