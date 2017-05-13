a=list()
with open('db.txt','r') as file:
	for i in file:
		a.append(i.strip())

b=input()
interval=len(a)
shift=0
c=None
while interval>=1:
	print(interval,end=' ')
	if interval%2:
		t=True
	else:
		t=False
	interval//=2
	contr=interval+shift-1
	if t:
		contr+=1
	if contr>=len(a):
		break
	print(shift,contr)
	if c==a[contr]:
		break
	c=a[contr]
	print(c,' | ',b)
	r=input()
	while r!=c and r!=b:
		r=input()
	if r==c:
		shift+=interval
		if t:
			shift+=1

a.append(b)
for i in range(shift+1,len(a))[::-1]:
	a[i],a[i-1]=a[i-1],a[i]
print(a)