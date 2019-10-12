import re


def check_phone(cont):
	if cont[0] == '8':
		cont = '7' + cont[1:]

	cont = re.sub('[^0-9]', '', cont)

	if not len(cont):
		raise Exception('not phone')

	return int(cont)


print(check_phone('8 (981) 163-55-78'))