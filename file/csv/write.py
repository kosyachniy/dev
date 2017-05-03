import csv

def write(text,name='db',sign=';'):
	with open(name+'.csv','w') as file:
		csv.writer(file,delimiter=sign,quotechar=' ',quoting=csv.QUOTE_MINIMAL).writerow(text)

if __name__=='__main__':
	write(input().split())