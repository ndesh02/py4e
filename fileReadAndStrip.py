name = input("Enter file:")
if len(name) < 1 : name = "mbox-short.txt"
handle = open(name)
r=0
counts=dict()

for line in handle:
    line=line.rstrip()
    lst=line.split()
    try:
        if lst[0]=='From':
            hours=lst[5].split(':')
            counts[hours[0]]=counts.get(hours[0],0)+1
    except:
        r=1
        continue

#sort by the key
lst=list()
for key,val in counts.items():
    newTup=(key,val)
    lst.append(newTup)

lst=sorted(lst)

for key,val in lst:
    print(key,val)
