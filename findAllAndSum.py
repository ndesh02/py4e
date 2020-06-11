import re
handle=open('regex_sum_656919.txt')
total=0
for lin in handle:
    lst=re.findall('[0-9]+',lin)
    for nums in lst:
        total=int(nums)+total

print(total)
