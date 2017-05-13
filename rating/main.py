a=list()
with open('db.txt','r') as file:
	for i in file:
		a.append(i.strip())

b=input()
interval=len(a)
shift=0
while interval>1:
	if interval%2:
		interval=(interval//2)+1
	else:
		interval//=2
	contr=interval+shift-1
	if contr>=len(a):
		break
	c=a[contr]
	print(c,' | ',b)
	r=input()
	while r!=c and r!=b:
		r=input()
	if r==c:
		shift+=interval

a.append(b)
for i in range(shift+1,len(a))[::-1]:
	a[i],a[i-1]=a[i-1],a[i]
print(a)