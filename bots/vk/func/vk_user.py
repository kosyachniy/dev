import json
import time

import vk_api
import requests


with open('keys.json', 'r') as file:
	data = json.loads(file.read())['vk']

	vk = vk_api.VkApi(login=data['login'], password=data['password'])
	vk.auth()


def max_size(lis, name='photo'):
	q = set(lis.keys())
	ma = 0

	if 'sizes' in q:
		for i, el in enumerate(lis['sizes']):
			if el['width'] > lis['sizes'][ma]['width']:
				ma = i

		return lis['sizes'][ma]['url']

	else:
		for t in q:
			if name + '_' in t and int(t[6:]) > ma:
				ma = int(t[6:])

		return lis[name + '_' + str(ma)]


# Отправить сообщение
def send(user, cont, img=[]):
	# Изображения
	for i in range(len(img)):
		if img[i][0:5] != 'photo':
			# Загружаем изображение на сервер
			if img[i].count('/') >= 3: # Если файл из интернета
				with open('re.jpg', 'wb') as file:
					file.write(requests.get(img[i]).content)
				img[i] = 're.jpg'

			# Загружаем изображение в ВК
			url = vk.method('photos.getMessagesUploadServer')['upload_url']

			response = requests.post(url, files={'photo': open(img[i], 'rb')})
			result = json.loads(response.text)

			photo = vk.method('photos.saveMessagesPhoto', {'server': result['server'], 'photo': result['photo'], 'hash': result['hash']})

			img[i] = 'photo{}_{}'.format(photo[0]['owner_id'], photo[0]['id'])

	req = {
		'random_id': int(time.time() * 1000000),
		'user_id': user,
		'message': cont,
		'attachment': ','.join(img),
	}

	return vk.method('messages.send', req)

# Последние непрочитанные сообщения
def read():
	messages = []
	for i in vk.method('messages.getConversations')['items']:
		if 'unread_count' in i['conversation']: # 'unanswered'
			messages.append((
				i['conversation']['peer']['id'],
				i['last_message']['text'],
				[max_size(j['photo']) for j in i['last_message']['attachments'] if j['type'] == 'photo'] if 'attachments' in i['last_message'] else [],
			))
	return messages

# Диалоги
def dial():
	messages = []

	offset = 0
	while True:
		conversations = vk.method('messages.getConversations', {
			'count': 200,
			'offset': offset,
		})['items']

		for i in conversations:
			messages.append(i['conversation']['peer']['id'])

		if len(conversations) < 200:
			break
		offset += 200

	return messages

# Информация о пользователе
def info(user):
	req = vk.method('users.get', {
		'user_ids': user,
		'fields': 'verified, first_name, last_name, sex, bdate, photo_id, country, city, home_town, screen_name, lang, phone, timezone',
	})[0]

	# Форматируем дату
	try:
		bd = req.get('bdate').count('.')
	except:
		bd = 0

	if bd == 2:
		bd = time.strftime('%Y%m%d', time.strptime(req['bdate'], '%d.%m.%Y'))
	elif bd == 1:
		bd = time.strftime('%m%d', time.strptime(req['bdate'], '%d.%m'))
	else:
		bd = 0

	data = {
		'verified': req.get('verified'),
		'name': req.get('first_name'),
		'surname': req.get('last_name'),
		'sex': req.get('sex'),
		'bd': int(bd),
		'photo': req.get('photo_id'),
		'geo': (str(req.get('country')['id']) if req.get('country') else '0') + '/' + (str(req.get('city')['id']) if req.get('city') else '0'),
		'id': user,
		'login': req.get('screen_name'),
		# 'language': data.get('lang'),
		# 'phone': data.get('phone'),
		# 'timezone': data.get('timezone'),
		# 'geo_home': data.get('home_town'),
	}

	return data

# Статистика сообщений
def stats():
	# messages = []
	timeline = {}

	offset = 0
	while True:
		conversations = vk.method('messages.getConversations', {
			'count': 200,
			'offset': offset,
		})['items']

		for i in conversations:
			id = i['conversation']['peer']['id']

			conversation = vk.method('messages.getHistory', {
				'peer_id': id,
			})

			# k = 0
			for j in conversation['items']:
				if j['out'] == 0:
					day = j['date'] // 86400
					# k += 1

					if day not in timeline:
						timeline[day] = {
							id: 1,
						}
					else:
						if id in timeline[day]:
							timeline[day][id] += 1
						else:
							timeline[day][id] = 1

			# messages.append(conversation)

		if len(conversations) < 200:
			break
		offset += 200

	stat = []
	line = sorted(list(timeline.keys()))
	for i in line:
		sum_mes = 0
		for j in timeline[i]:
			sum_mes += timeline[i][j]

		stat.append((i, len(timeline[i]), sum_mes))

	return stat

# Посты
def wall(group, post=0):
	res = vk.method('wall.get', {'owner_id': group})['items']

	res = [{
		'id': el['id'],
		'text': el['text'],
		'attachments': [max_size(i['photo']) for i in el['attachments'] if i['type'] == 'photo'] if 'attachments' in el else [],
	} for el in res if el['id'] > post]

	return res[::-1]

# Группы
def groups():
	res = vk.method('groups.get')['items']
	res = vk.method('groups.getById', {'group_ids': ','.join(map(str, res))})

	res = [{
		'id': el['id'],
		'login': el['screen_name'],
		'name': el['name'],
	} for el in res]

	return res