import time

from func.vk_group import read, send


while True:
	try:
		new_message = read()

	except:
		print('Ошибка чтения!')
		time.sleep(5)

	else:
		for i in new_message:
			print(info(i[0]))
			send(i[0], 'чё надо')

	time.sleep(1)