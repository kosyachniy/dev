a=list()
with open('db.txt','r') as file:
	for i in file:
		a.append(i.strip())

b=input()
interval=len(a)
shift=0
c=None
while interval>=1:
	if interval%2:
		i=(interval//2)+shift+1
	else:
		i=interval//2+shift
	'''
	t=interval%2
	if t:
		interval+=1
	interval//=2
	contr=interval+shift-1
	if contr>=len(a) or c==a[contr]:
		break
	c=a[contr]
	print(interval,shift,contr)
	'''
	if i>len(a):
		break
	c=a[i-1]
	print(interval,shift,i)
	print('1 - ',c,'  |  2 - ',b)
	r=input()
	while r!='1' and r!='2':
		r=input()
	if r=='1':
		interval//=2
		shift+=i
	else:
		if interval%2:
			interval//=2
		else:
			interval=(interval//2)-1

a.append(b)
for i in range(shift+1,len(a))[::-1]:
	a[i],a[i-1]=a[i-1],a[i]

print(a)
'''
with open('db.txt','w') as file:
	for i in range(len(a)-1):
		print(a[i],file=file)
	print(a[len(a)-1],end='',file=file)
'''