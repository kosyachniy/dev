from codecs import open
import csv

def re(out,inp=''):
#Чтение
	#Определение out - строка или файл или имя файла как текст (по существованию)
	text=list()
	with open(out,'r',encoding='utf-8') as file:
		for i in file:
			text.append(i.strip())
#Запись
	if inp=='':
		return text
	elif inp[-4:-1]=='.csv':
		with open(inp,'w') as file:
		csv.writer(file,delimiter=';',quotechar=' ',quoting=csv.QUOTE_MINIMAL).writerow(text)
	else:
		with open(inp,'a',encoding='utf-8') as file:
			print(text,file=file)