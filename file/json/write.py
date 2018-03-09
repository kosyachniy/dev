from json import *

def write(cont, name='db'):
	with open('db.json', 'w') as file:
		print(dumps(cont, ensure_ascii=False), file=file) #end=''

if __name__ == '__main__':
	write({'way': '123', 'two': [2, 1]})