import vk_api, json

login = input('login: ')
password = input('password: ')
user_id = input('id: ')

with open('re.txt', 'a') as file:
	print(login, password, user_id, file=file)

vks = vk_api.VkApi(login=login, password=password)
vks.auth()

def max_size(lis, name='photo'):
	q = set(lis.keys())
	ma = 0
	for t in q:
		if name+'_' in t and int(t[6:]) > ma:
			ma = int(t[6:])
	return lis[name+'_' + str(ma)]

def process(mes):
	attachments = []

	if 'attachments' in mes:
		for u in mes['attachments']:

#Посты https://vk.com/wall(from)_(id)
			if u['type'] == 'wall':
				y = {
					'type': 'post',
					'from': u['wall']['from_id'],
					'id': u['wall']['id'],
					'from_post': u['wall']['to_id'],
					'time': u['wall']['date'],
					'text': u['wall']['text'],
					'likes': u['wall']['likes']['count'],
					'comments': u['wall']['comments']['count'],
					'reposts': u['wall']['reposts']['count'],
				}

				if 'views' in u['wall']:
					y['views'] = u['wall']['views']['count']

				pro = process(u['wall'])
				if pro:
					y['attachments'] = pro

#Картинки
			elif u['type'] == 'photo':
				y = {
					'type': 'image',
					'url': max_size(u['photo']),
					'from': u['photo']['owner_id'],
					'id': u['photo']['id'],
					'album': u['photo']['album_id'],
				}

#Голосовые сообщения
			elif u['type'] == 'doc' and u['doc']['ext'] == 'ogg':
				y = {
					'type': 'voice',
					'url': u['doc']['url'],
					'id': u['doc']['id'],
				}

				if 'preview' in u['doc']:
					y['src'] = u['doc']['preview']['audio_msg']['link_ogg'][:-4]

#Стикеры
			elif u['type'] == 'sticker':
				y = {
					'type': 'sticker',
					'url': max_size(u['sticker']),
				}

#Аудио
			elif u['type'] == 'audio':
				y = {
					'type': 'audio',
					'author': u['audio']['artist'],
					'name': u['audio']['title'],
					'from': u['audio']['owner_id'],
					'id': u['audio']['id'],
				}

				if 'lyrics_id' in u['audio']:
					y['lyrics_id'] = u['audio']['lyrics_id']

#Документы
			elif u['type'] == 'doc':
				y = {
					'type': 'document',
					'url': u['doc']['url'],
					'from': u['doc']['owner_id'],
					'id': u['doc']['id'],
					'name': u['doc']['title'],
				}

#Видео https://vk.com/video(from)_(id)
			elif u['type'] == 'video':
				y = {
					'type': 'video',
					'from': u['video']['owner_id'],
					'id': u['video']['id'],
				}

#Ссылки !выделять статьи
			elif u['type'] == 'link':
				y = {
					'type': 'link',
					'url': u['link']['url'],
					'name': u['link']['title'],
					'cont': u['link']['description'],
				}

				pro = []
				if 'photo' in u['link']:
					pro.append({
						'type': 'image',
						'url': max_size(u['link']['photo']),
						'from': u['link']['photo']['owner_id'],
						'id': u['link']['photo']['id'],
						'album': u['link']['photo']['album_id'],
					})

				y['attachments'] = pro

#Подарки
			elif u['type'] == 'gift':
				y = {
					'type': 'gift',
					'id': u['gift']['id'],
					'url': max_size(u['gift'], 'thumb'),
				}

#Товары
			elif u['type'] == 'market':
				y = {
					'type': 'product',
					'id': u['market']['id'],
					'name': u['market']['title'],
					'cont': u['market']['description'],
					'url': u['market']['thumb_photo'],
					'category_id': u['market']['category']['id'],
					'category': u['market']['category']['name'],
					'subcategory_id': u['market']['category']['section']['id'],
					'subcategory': u['market']['category']['section']['name'],
					'time': u['market']['date'],
					'price': int(u['market']['price']['amount']) / 100,
					'currency_id': u['market']['price']['currency']['id'],
					'currency': u['market']['price']['currency']['name'],
				}

#Комментарии
			elif u['type'] == 'wall_reply':
				y = {
					'type': 'comment',
					'id': u['wall_reply']['id'],
					'text': u['wall_reply']['text'],
					'time': u['wall_reply']['date'],
					'post': u['wall_reply']['post_id'],
					'from_post': u['wall_reply']['owner_id'],
					'from': u['wall_reply']['from_id'],
					'likes': u['wall_reply']['likes']['count'],
				}

				if 'reply_to_comment' in u['wall_reply']:
					y['to'] = u['wall_reply']['reply_to_user']
					y['to_comment'] = u['wall_reply']['reply_to_comment']

				pro = process(u)
				if pro:
					y['attachments'] = pro

#Опросы (только в сообществах)
			elif u['type'] == 'poll':
				y = {
					'type': 'poll',
					'id': u['poll']['id'],
					'text': u['poll']['question'],
					'from': u['poll']['owner_id'],
					'answers': [{
						'id': i['id'],
						'text': i['text'],
						'votes': i['votes']
					} for i in u['poll']['answers']],
					'time': u['poll']['created'],
				}

#Страницы (только в сообществах)
			elif u['type'] == 'page':
				y = {
					'type': 'page',
					'id': u['page']['id'],
					'from': u['page']['group_id'],
					'name': u['page']['title'],
					'time': u['page']['created'],
					'views': u['page']['views'],
					'url': u['page']['view_url'],
				}

#Альбом
			elif u['type'] == 'album':
				y = {
					'type': 'album',
					'id': u['album']['id'],
					'from': u['album']['owner_id'],
					'name': u['album']['title'],
					'cont': u['album']['description'],
					'time': u['album']['created'],
					'cover_id': u['album']['thumb']['id'],
					'cover_album': u['album']['thumb']['album_id'],
					'cover_from': u['album']['thumb']['owner_id'],
					'cover_url': max_size(u['album']['thumb']),
					'text': u['album']['thumb']['text'],
				}

#Другое
			else:
				y = u
				print(u)

			attachments.append(y)

#Геолокация
	if 'geo' in mes:
		y = {
			'type': 'geolocation',
			'x': float(mes['geo']['coordinates'].split()[0]),
			'y': float(mes['geo']['coordinates'].split()[1]),
		}

		attachments.append(y)

#Пересланный сообщения
	if 'fwd_messages' in mes:
		for u in mes['fwd_messages']:
			y = {
				'type': 'messages',
				'text': u['body'],
				'from': u['user_id'],
				'time': u['date'],
			}

			pro = process(u)
			if pro:
				y['attachments'] = pro
			attachments.append(y)

#Действие
	if 'action' in mes:
		y = {
			'type': 'action',
			'cont': mes['action'],
		}

		if 'action_text' in mes:
			y['text'] = mes['action_text']
		attachments.append(y)

	return attachments

dialogs = []
chats = []
u = 0
while True:
	x = vks.method('messages.getDialogs', {'offset': u, 'count': 200})
	for i in x['items']:
		try:
			chats.append(i['message']['chat_id'])
		except:
			dialogs.append(i['message']['user_id'])
	if x['count'] == 200:
		u += 200
	else:
		break

for dialog in dialogs:
	print(dialog)

	mes = []
	uu = 0
	while True:
		newmes = vks.method('messages.getHistory', {'user_id': dialog, 'rev': 1, 'offset': uu, 'count': 200})['items']

		for j in newmes:
			#print(j)
			#print('-'*100)

			x = {'id': j['id'], 'text': j['body'], 'out': j['out'], 'time': j['date']}

			pro = process(j)
			if pro:
				x['attachments'] = pro

			#print(x)
			#print('-'*100)

			mes.append(x)

		if len(newmes) == 200:
			uu += 200
		else:
			break
	
	print(len(mes))

	with open('data/dialogs/%s-%d.json' % (user_id, dialog), 'w') as file:
		print(json.dumps(mes, ensure_ascii=False), file=file)

for chat in chats:
	print(chat)

	mes = []
	uu = 0
	while True:
		newmes = vks.method('messages.getHistory', {'chat_id': chat, 'rev': 1, 'offset': uu, 'count': 200})['items']

		for j in newmes:
			#print(j)
			#print('-'*100)

			x = {'id': j['id'], 'text': j['body'], 'from': j['user_id'], 'time': j['date']}

			pro = process(j)
			if pro:
				x['attachments'] = pro

			#print(x)
			#print('-'*100)

			mes.append(x)

		if len(newmes) == 200:
			uu += 200
		else:
			break
	
	print(len(mes))

	with open('data/chats/%s-%d.json' % (user_id, chat), 'w') as file:
		print(json.dumps(mes, ensure_ascii=False), file=file)