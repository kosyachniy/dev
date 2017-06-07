from json import *

a=dumps({'way':'123', 'two':[2,1]}, indent=4)
with open('db.txt', 'w') as file:
	print(a, file=file, end='')