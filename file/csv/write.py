import csv
import numpy as np

def write(data, name='db', sign=','):
	# Для записи множеств
	if type(data) in (list, tuple) and type(data[0]) in (set, frozenset):
		data = [tuple(i) for i in data]

	# Для записи матриц
	if type(data) not in (list, tuple) or type(data[0]) not in (list, tuple):
		data = [data]

	with open(name+'.csv', 'a') as file:
		for i in data:
			csv.writer(file, delimiter=sign, quotechar=' ', quoting=csv.QUOTE_MINIMAL).writerow(i)

if __name__=='__main__':
	# write(((1,2,3),(4,5,6),(7,8,9)))
	write(({1,2,3},{4,5,6},{7,8,9}))
	# write(input().split())