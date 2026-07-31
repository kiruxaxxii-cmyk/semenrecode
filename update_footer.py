with open('assets/index-BKmpLbls.js', 'r', encoding='utf-8') as f:
    content = f.read()

target = 'u.jsxs("p",{children:["Contact: ",u.jsx("a",{href:`mailto:${a}`,children:a})]})'
replacement = 'u.jsxs("p",{children:[u.jsx("a",{href:"https://t.me/svitik322",children:"@svitik322"})," | Protection by CabbitGuard , Desigined by @svitik322 and @virtukid"]})'

if target in content:
    content = content.replace(target, replacement)
    with open('assets/index-BKmpLbls.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success")
else:
    print("Target not found!")
