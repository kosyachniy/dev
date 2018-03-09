from json import *

def read(file='db'):
	with open(name+'.json', 'r') as file:
		return loads(file.read())

if __name__ == '__main__':
	print(read())