a=list()
with open('db.txt','r') as file:
	for i in file:
		a.append(i.strip())

for i in range(len(a)-1):
	print(a[i],' | ',a[i+1])
	r=input()
	while r!=a[i] and r!=a[i+1]:
		r=input()
	if a[i+1]==r:
		a[i],a[i+1]=a[i+1],a[i]

print(a)