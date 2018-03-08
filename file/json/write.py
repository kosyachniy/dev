from json import *

a = dumps({'way': '123', 'two': [2, 1]}, ensure_ascii=False)
with open('db.json', 'w') as file:
	print(a, file=file, end='')