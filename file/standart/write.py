from codecs import open #Для кодировки

text = input()
with open('db.txt', 'a', encoding='utf-8') as file:
	print(text, file=file)