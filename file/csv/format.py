import sys, csv

def text(x):
	y = []

	sys.path.append('../syntax')
	from parse import parse

	for i in parse(x):
		for j in i.word:
			if j['speech'] != 'sign': #Без символов
				y.append(j['infinitive'])
	return y

def format(name='db', sign=','):
	with open(name+'.txt', 'r') as out:
		with open(name+'.csv', 'w') as file:
			a = csv.writer(file, delimiter=sign, quotechar=' ', quoting=csv.QUOTE_MINIMAL) #Сделать через ;
			for i in out:
				a.writerow(text(i.strip())) #Изменить кодировку с русским языком

if __name__=='__main__':
	format()