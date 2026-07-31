with open('assets/index-BKmpLbls.js', 'r', encoding='utf-8') as f:
    content = f.read()
    
idx = content.find('help@newcode.fun')
if idx != -1:
    print(content[max(0, idx-300):min(len(content), idx+500)])
else:
    print("Not found")
