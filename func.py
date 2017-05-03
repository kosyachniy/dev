from codecs import open
import csv,os

def re(out,inp=''):
#Чтение
	#Определение out - строка или файл или имя файла как текст (по существованию)
	if os.path.exists(out):
		text=list()
		if out[-4:-1]=='.csv':
			###
		else:
			with open(out,'r',encoding='utf-8') as file:
				for i in file:
					text.append(i.strip())
	else:
		text=out
#Запись
	if inp=='':
		return text
	elif inp[-4:-1]=='.csv':
		with open(inp,'w') as file:
		csv.writer(file,delimiter=';',quotechar=' ',quoting=csv.QUOTE_MINIMAL).writerow(text)
	else:
		with open(inp,'a',encoding='utf-8') as file:
			print(text,file=file)