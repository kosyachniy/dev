import json

def read(name='db'):
	with open(name + '.json', 'r') as file:
		return json.loads(file.read())

if __name__ == '__main__':
	print(read('sets'))