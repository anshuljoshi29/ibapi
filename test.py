import re

text = "(Property ID:SBIN037585638997) Property Visited:115 times"

data = r"Property ID:(.+?)\)"
match = re.search(data, text)

if match:
    print(match.group(1))
else:
    print("No match")
