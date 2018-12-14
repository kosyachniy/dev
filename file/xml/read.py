from func.xml import from_xml


def read(name='db'):
	with open(name + '.xml', 'r') as file:
		return from_xml(file.read())


if __name__ == '__main__':
	print(read())