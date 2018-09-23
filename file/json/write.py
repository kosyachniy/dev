import json

def write(cont, name='db'):
	with open(name + '.json', 'w') as file:
		print(json.dumps(cont, ensure_ascii=False, indent='\t'), file=file)

if __name__ == '__main__':
	write({'name': 'текст', 'cont': [2, 1]}, 'sets')