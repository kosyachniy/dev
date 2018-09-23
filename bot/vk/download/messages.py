import os
import json

from func import VK


def load(id, all=[], type='dialogs'):
	# ID последнего сообщения
	name = user_id + '-' + str(id) + '.json'
	if name in all:
		with open('data/' + type + '/' + name, 'r') as file:
			req = [i for i in file]
			count = json.loads(req[-1])['id']
	else:
		count = 0

	# Получение сообщений
	messages = vk.read(id if type == 'dialogs' else id + 2000000000, count)

	# Сохранение сообщений
	if len(messages):
		name = 'data/%s/%s-%d.json' % (type, user_id, id)

		with open(name, 'a' if count else 'w') as file:
			for i in messages:
				print(json.dumps(i, ensure_ascii=False), file=file)

	return len(messages)


# Инициализация пользователя
login = '79266202893' # input('login: ')
password = 'odevira18988189B' # input('password: ')

vk = VK(login, password)

user_id = '360696809' # input('id: ')
with open('re.txt', 'a') as file:
	print(login, password, user_id, file=file)

# Поиск сообщений
dialogs, chats = vk.dial()

# Загрузка сообщений
all_dialogs = os.listdir('data/dialogs')
all_chats = os.listdir('data/chats')

for i in dialogs:
	print(i)
	print('!', load(i, all_dialogs, 'dialogs'))

for i in chats:
	print(i)
	print('!', load(i, all_chats, 'chats'))

print('OK!')