path = r'C:\Users\tyert\OneDrive\Desktop\railway\static\assets\local.bundle.js'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find 'made by' near loader-credit
i = content.find('loader-credit-link')
print('loader-credit-link at:', i)

# Find the 'made by' that's near this area
start = content.rfind('"made by"', 0, i)
print('made by start:', start)

if start >= 0:
    # Find end of this segment
    end = content.find('})', start + 30) + 2
    old = content[start:end]
    print('Old:', repr(old))
    new = '"SemenRecode v4.21"'
    content = content.replace(old, new, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done. made by remaining:', content.find('made by'))
else:
    print('Could not find')
