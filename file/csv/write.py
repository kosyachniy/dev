import csv

def write(text,name='db'):
	with open(name+'.csv','w') as file:
		csv.writer(file,quotechar=' ',quoting=csv.QUOTE_MINIMAL).writerow(text.strip())

if __name__=='__main__':
	write(input())