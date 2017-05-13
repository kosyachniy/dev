a=list()
with open('db.txt','r') as file:
	for i in file:
		a.append(i.strip())

b=input()
interval=len(a)
shift=0
c=None
while interval>=1:
	t=interval%2
	interval//=2
	contr=interval+shift
	if not t:
		contr-=1
	if c==a[contr]:
		break
	c=a[contr]
	print('1 - ',c,'  |  2 - ',b)
	r=int(input())
	while r!=1 and r!=2:
		r=int(input())
	if r==1:
		shift+=interval
		if t:
			shift+=1

a.append(b)
for i in range(shift+1,len(a))[::-1]:
	a[i],a[i-1]=a[i-1],a[i]

with open('db.txt','w') as file:
	for i in a:
		print(i,file=file)