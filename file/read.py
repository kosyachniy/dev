from codecs import open #Для кодировки

with open('data.txt','r',encoding='utf-8') as file:
	text=file.getline()
	print(text)
