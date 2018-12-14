from func.json import from_json


def read(name='db'):
	with open(name + '.json', 'r') as file:
		return from_json(file.read())


if __name__ == '__main__':
	print(read('sets'))