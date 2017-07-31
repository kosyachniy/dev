a=list()
with open('db.txt', 'r') as file:
	for i in file:
		a.append(i.strip())

b=input()
interval=len(a)
shift=0
while interval>=1:
	t=interval%2
	interval//=2
	i=interval+t
	print('1 - ', a[i+shift-1], '  |  2 - ', b)
	r=input()
	while r!='1' and r!='2':
		r=input()
	if r=='1':
		shift+=i
	else:
		if not t:
			interval-=1

a.append(b)
for i in range(shift+1,len(a))[::-1]:
	a[i], a[i-1]=a[i-1], a[i]

with open('db.txt', 'w') as file:
	for i in range(len(a)-1):
		print(a[i], file=file)
	print(a[len(a)-1], end='', file=file)