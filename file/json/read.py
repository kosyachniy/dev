from json import *

with open('db.json', 'r') as file:
	a = file.read()
print(loads(a))