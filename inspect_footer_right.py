import re

with open('assets/index-BKmpLbls.js', 'r', encoding='utf-8', errors='ignore') as f:
    js = f.read()

idx = js.find('footer-legal-copy')
if idx != -1:
    print(js[max(0, idx-100):min(len(js), idx+500)])
