from func.xml import to_xml


def write(cont, name='db'):
	with open(name + '.xml', 'w') as file:
		print(to_xml(cont), file=file)


if __name__ == '__main__':
	write({'name': 'текст', 'cont': [2, 1]})