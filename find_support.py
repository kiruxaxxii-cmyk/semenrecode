with open('assets/index-BKmpLbls.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# We need to find the exact string for the Support column in the footer.
# Let's search for "Поддержка" and extract the array assignment.

match = re.search(r'l=\[\{title:(.+?)\}\];', content)
if match:
    full_array = match.group(0)
    print("Found array:", full_array)
else:
    # try another way
    match = re.search(r'l=\[\{title:.*?\}\];', content)
    if match:
        print("Found array:", match.group(0))
    else:
        print("Could not find array.")
