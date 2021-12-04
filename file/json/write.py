from func.json import to_json


def write(cont, name='db'):
	with open(name + '.json', 'w', encoding='utf-8') as file:
		print(to_json(cont), file=file)


if __name__ == '__main__':
	write({'name': 'текст', 'cont': [2, 1]}, 'sets')