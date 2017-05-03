import csv

def format(name='db'):
	with open(name+'.txt','r') as out:
		with open(name+'.csv','w') as file:
			a=csv.writer(file,quotechar=' ',quoting=csv.QUOTE_MINIMAL)
			for i in out:
				a.writerow(i.strip())

if __name__=='__main__':
	format()