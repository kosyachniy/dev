import re


template = re.compile(r'\S+@\S+\.\S+')

def is_mail(cont):
	return template.match(cont) != None

def check_mail(cont):
	return re.match('.+@.+\..+', cont) != None


if __name__ == '__main__':
	print(is_mail(input()))
	print(is_mail('polozhev@mail.ru'))