import csv


def read_file(name, sign=','):
	with open('{}.csv'.format(name), 'r') as file:
		return list(csv.reader(file, delimiter=sign, quotechar=' '))

def read_data(name, skip=1, sign=','):
	with open('data/{}.csv'.format(name), 'r') as file:
		data = list(csv.reader(file, delimiter=sign, quotechar=' '))[skip:]
		return list(map(lambda x: list(map(float, x)), data))


if __name__=='__main__':
	print(read_file('db'))