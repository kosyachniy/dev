import json
import time

import vk_api
import requests


def max_size(lis, name='photo'):
	if 'images' in lis:
		ma = 0
		for j in lis['images']:
			if j['width'] > ma:
				re = j['url']
				ma = j['width']
		return re

	else:
		q = set(lis.keys())
		ma = 0
		for t in q:
			if name + '_' in t and int(t[6:]) > ma:
				ma = int(t[6:])
		return lis[name + '_' + str(ma)]

# Работа с вложениями

def process(mes):
	attachments = []

	if 'attachments' in mes:
		for u in mes['attachments']:

# Посты https://vk.com/wall(from)_(id)
			if u['type'] == 'wall':
				y = {
					'type': 'post',
					'id': u['wall']['id'],
					'from': u['wall']['from_id'],
					'time': u['wall']['date'],
					'text': u['wall']['text'],
					'from_post': u['wall']['to_id'],
					'likes': u['wall']['likes']['count'],
					'comments': u['wall']['comments']['count'],
					'reposts': u['wall']['reposts']['count'],
				}

				if 'views' in u['wall']:
					y['views'] = u['wall']['views']['count']

				pro = process(u['wall'])
				if pro:
					y['attachments'] = pro

# Картинки
			elif u['type'] == 'photo':
				y = {
					'type': 'image',
					'url': max_size(u['photo']),
					'id': u['photo']['id'],
					'from': u['photo']['owner_id'],
					'album': u['photo']['album_id'],
				}

# Голосовые сообщения
			elif u['type'] == 'doc' and u['doc']['ext'] == 'ogg':
				y = {
					'type': 'voice',
					'url': u['doc']['url'],
					'id': u['doc']['id'],
				}

				if 'preview' in u['doc']:
					y['src'] = u['doc']['preview']['audio_msg']['link_ogg'][:-4]

# Стикеры
			elif u['type'] == 'sticker':
				y = {
					'type': 'sticker',
					'url': max_size(u['sticker']),
					'id': u['sticker']['sticker_id'],
				}

# Аудио
			elif u['type'] == 'audio':
				y = {
					'type': 'audio',
					'id': u['audio']['id'],
					'from': u['audio']['owner_id'],
					'name': u['audio']['title'],
					'author': u['audio']['artist'],
				}

				if 'lyrics_id' in u['audio']:
					y['lyrics_id'] = u['audio']['lyrics_id']

# Документы
			elif u['type'] == 'doc':
				y = {
					'type': 'document',
					'url': u['doc']['url'],
					'id': u['doc']['id'],
					'from': u['doc']['owner_id'],
					'name': u['doc']['title'],
				}

# Видео https://vk.com/video(from)_(id)
			elif u['type'] == 'video':
				y = {
					'type': 'video',
					'id': u['video']['id'],
					'from': u['video']['owner_id'],
				}

# Ссылки !выделять статьи и альбомы музыки
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
						'id': u['link']['photo']['id'],
						'from': u['link']['photo']['owner_id'],
						'album': u['link']['photo']['album_id'],
					})

				y['attachments'] = pro

# Подарки
			elif u['type'] == 'gift':
				y = {
					'type': 'gift',
					'url': max_size(u['gift'], 'thumb'),
					'id': u['gift']['id'],
				}

# Товары
			elif u['type'] == 'market':
				y = {
					'type': 'product',
					'url': u['market']['thumb_photo'],
					'id': u['market']['id'],
					'name': u['market']['title'],
					'time': u['market']['date'],
					'cont': u['market']['description'],
					'category_id': u['market']['category']['id'],
					'category': u['market']['category']['name'],
					'subcategory_id': u['market']['category']['section']['id'],
					'subcategory': u['market']['category']['section']['name'],
					'price': int(u['market']['price']['amount']) / 100,
					'currency_id': u['market']['price']['currency']['id'],
					'currency': u['market']['price']['currency']['name'],
				}

# Комментарии
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

# Перевод денег

# Опросы (только в сообществах)
			elif u['type'] == 'poll':
				y = {
					'type': 'poll',
					'id': u['poll']['id'],
					'from': u['poll']['owner_id'],
					'time': u['poll']['created'],
					'text': u['poll']['question'],
					'answers': [{
						'id': i['id'],
						'text': i['text'],
						'votes': i['votes']
					} for i in u['poll']['answers']],
				}

# Страницы (только в сообществах)
			elif u['type'] == 'page':
				y = {
					'type': 'page',
					'id': u['page']['id'],
					'from': u['page']['group_id'],
					'time': u['page']['created'],
					'name': u['page']['title'],
					'views': u['page']['views'],
					'url': u['page']['view_url'],
				}

# Альбомы картинок (только в сообществах)
			elif u['type'] == 'album':
				y = {
					'type': 'album',
					'id': u['album']['id'],
					'from': u['album']['owner_id'],
					'time': u['album']['created'],
					'text': u['album']['thumb']['text'],
					'name': u['album']['title'],
					'cont': u['album']['description'],
					'cover_id': u['album']['thumb']['id'],
					'cover_album': u['album']['thumb']['album_id'],
					'cover_from': u['album']['thumb']['owner_id'],
					'cover_url': max_size(u['album']['thumb']),
				}

# Другое
			else:
				y = u
				print(u)

			attachments.append(y)

# Геолокация
	if 'geo' in mes:
		y = {
			'type': 'geolocation',
			'x': float(mes['geo']['coordinates'].split()[0]),
			'y': float(mes['geo']['coordinates'].split()[1]),
		}

		attachments.append(y)

# Пересланные сообщения
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

# Действия (только в чатах)
	if 'action' in mes:
		y = {
			'type': 'action',
			'cont': mes['action'],
		}

		if 'action_text' in mes:
			y['text'] = mes['action_text']
		attachments.append(y)

	return attachments


class VK:
	def __init__(self, login, password):
		self.vk = vk_api.VkApi(login=login, password=password)
		self.vk.auth()

	# # Отправить сообщение
	# def send(self, user, cont, img=[]):
	# 	# Изображения
	# 	for i in range(len(img)):
	# 		if img[i][0:5] != 'photo':
	# 			# Загружаем изображение на сервер
	# 			if img[i].count('/') >= 3: # Если файл из интернета
	# 				with open('re.jpg', 'wb') as file:
	# 					file.write(requests.get(img[i]).content)
	# 				img[i] = 're.jpg'

	# 			# Загружаем изображение в ВК
	# 			url = vk.method('photos.getMessagesUploadServer')['upload_url']

	# 			response = requests.post(url, files={'photo': open(img[i], 'rb')})
	# 			result = json.loads(response.text)

	# 			photo = vk.method('photos.saveMessagesPhoto', {'server': result['server'], 'photo': result['photo'], 'hash': result['hash']})

	# 			img[i] = 'photo{}_{}'.format(photo[0]['owner_id'], photo[0]['id'])

	# 	req = {
	# 		'user_id': user,
	# 		'message': cont,
	# 		'attachment': ','.join(img),
	# 	}

	# 	return vk.method('messages.send', req)

	# Список всех диалогов
	def dial(self):
		dialogs = []
		chats = []

		offset = 0
		while True:
			conversations = self.vk.method('messages.getConversations', {
				'count': 200,
				'offset': offset,
			})['items']

			for i in conversations:
				if i['conversation']['peer']['type'] == 'chat':
					chats.append(i['conversation']['peer']['local_id'])
				else:
					dialogs.append(i['conversation']['peer']['id'])

			if len(conversations) < 200:
				break
			offset += 200

		return dialogs, chats

	# Все сообщения
	def read(self, id, start=0):
		messages = []
		offset = 0

		while True:
			newmes = self.vk.method('messages.getHistory', {
				'peer_id': id,
				'rev': 1,
				'offset': offset,
				'count': 200,
			})['items']

			for j in newmes:
				if j['id'] <= start:
					continue

				x = {
					'id': j['id'],
					'text': j['body'],
					'time': j['date'],
				}

				#!
				if id < 2000000000:
					x['out'] = j['out']
				else:
					x['from'] = j['user_id']

				attachments = process(j)
				if len(attachments):
					x['attachments'] = attachments

				messages.append(x)

			if len(newmes) < 200:
				break
			offset += 200
		
		return messages