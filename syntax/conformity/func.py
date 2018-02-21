import csv

def delete(name):
	with open('data/'+name+'.csv', 'w') as file:
		pass

def write(text, name='db', sign=','):
	with open('data/'+name+'.csv', 'a') as file:
		csv.writer(file, delimiter=sign, quotechar=' ', quoting=csv.QUOTE_MINIMAL).writerow(text)

def read(name, sign=','):
	with open('data/'+name+'.csv', 'r') as file:
		return [i for i in csv.reader(file, delimiter=sign, quotechar=' ')]