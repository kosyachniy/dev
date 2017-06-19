from json import *

with open('db.txt', 'r') as file:
	a=file.read()
print(loads(a))