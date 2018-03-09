from codecs import open #Для кодировки

with open('db.txt', 'r', encoding='utf-8') as file:
	print(file.read())
#.strip()