import csv

def read(name='db', sign=';'):
	with open(name+'.csv', 'r') as file:
		return [i for i in csv.reader(file, delimiter=sign, quotechar=' ')]

if __name__=='__main__':
	print(read())