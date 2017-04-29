from codecs import open #Для кодировки

text=input()
with open('data.txt','a',encoding='utf-8') as file:
	print(text,file=file)