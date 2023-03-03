import re

# Your code goes here
find_members = [func for func in dir(re) if "find" in func]
find_members.sort()

for member in find_members:
    print(member)
