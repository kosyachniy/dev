from flask import request
from app import app

import time, base64
from mongodb import *
from re import findall, match
from hashlib import md5
from json import dumps
from random import randint
from os import listdir, remove

generate = lambda length=32: ''.join([chr(randint(48, 123)) for i in range(length)])
on = lambda x, y: all([i in x for i in y])

def max_image(url):
	x = listdir(url)
	k = 0
	for i in x:
		j = findall(r'\d+', i)
		if len(j) and int(j[0]) > k:
			k = int(j[0])
	return k+1

def load_image(url, data, adr=None, format='jpg', type='base64'):
	if type == 'base64':
		data = base64.b64decode(data)

	id = adr if adr else max_image(url)
	with open('%s/%d.%s' % (url, id, format), 'wb') as file:
		file.write(data)

	return id


@app.route('/', methods=['POST'])
def process():
	x = request.json
	#print(x)

	if 'method' not in x:
		return '2'

	#Убираем лишние отступы
	for i in x:
		if type(x[i]) == str:
			x[i] = x[i].strip()

	#Определение пользователя
	if 'token' in x:
		user = db['tokens'].find_one({'token': x['token']})['id']
	else:
		user = 0

	try:
#Регистрация
		if x['method'] == 'profile.reg':
			#Не все поля заполнены
			if not on(x, ('login', 'pass', 'mail')):
				return '3'

			x['login'] = x['login'].lower()

			#Логин существует
			if len(list(db['users'].find({'login': x['login']}))):
				return '5'

			#Недопустимый логин
			if not 3 <= len(x['login']) <= 20 or len(findall('[^a-z0-9]', x['login'])) or not len(findall('[a-z]', x['login'])):
				return '4'

			#Почта зарегистрирована
			if len(list(db['users'].find({'mail': x['mail']}))):
				return '8'

			#Недопустимый пароль
			if not 6 <= len(x['pass']) <= 40 or len(findall('[^a-zA-z0-9!@#$%^&*()-_+=;:,./?\|`~\[\]{}]', x['pass'])) or not len(findall('[a-zA-Z]', x['pass'])) or not len(findall('[0-9]', x['pass'])):
				return '6'

			#Это не почта
			if match('.+@.+\..+', x['mail']) == None:
				return '7'

			#Неправильное имя
			if 'name' in x and not x['name'].isalpha():
				return '9'

			#Неправильная фамилия
			if 'surname' in x and not x['surname'].isalpha():
				return '10'

			try:
				id = db['users'].find().sort('id', -1)[0]['id'] + 1
			except:
				id = 1

			db['users'].insert({
				'id': id,
				'login': x['login'],
				'password': md5(bytes(x['pass'], 'utf-8')).hexdigest(),
				'mail': x['mail'],
				'name': x['name'].title() if 'name' in x else None,
				'surname': x['surname'].title() if 'surname' in x else None,
				'rating': 0,
			})

			token = generate()
			db['tokens'].insert({'token': token, 'id': id, 'time': time.time()})

			return dumps({'id': id, 'token': token})

# db['users'].insert({
# 	'id': 1,
# 	'login': 'kosyachniy',
# 	'password': '<md5>',
# 	'name': 'Алексей',
# 	'surname': 'Полоз',
# 	'rating': 0,
# 	'mail': 'polozhev@mail.ru',
# 	'description': 'Косячь пока косячится',
# 	'admin': 8,
# })

# 0 - удалён | 1 - заблокирован | 2 - не авторизован | 3 - обычный | 4 - продвинутый | 5 -  корректор | 6 - модератор | 7 - администратор | 8 - владелец

#Авторизация
		elif x['method'] == 'profile.auth':
			#Не все поля заполнены
			if not on(x, ('login', 'pass')):
				return '3'

			x['login'] = x['login'].lower()

			#Логин не существует
			if not len(list(db['users'].find({'login': x['login']}))):
				return '4'

			i = db['users'].find_one({'login': x['login'], 'password': md5(bytes(x['pass'], 'utf-8')).hexdigest()})
			if i:
				id = i['id']

			#Неправильный пароль
			else:
				return '5'

			token = generate()
			db['tokens'].insert({'token': token, 'id': id, 'time': time.time()})

			return dumps({'id': id, 'token': token})

#Изменение личной информации
		elif x['method'] == 'profile.edit':
			#Не все поля заполнены
			if not on(x, ('token',)):
				return '3'

			i = db['tokens'].find_one({'token': x['token']})
			if i:
				id = i['id']

			#Несуществует токен
			else:
				return '4'

			i = db['users'].find_one({'id': id})

			if 'name' in x:
				#Неправильное имя
				if not x['name'].isalpha():
					return '5'

				i['name'] = x['name'].title()

			if 'surname' in x:
				#Неправильная фамилия
				if not x['surname'].isalpha():
					return '6'

				i['surname'] = x['surname'].title()

			if 'description' in x: i['description'] = x['description']
			db['users'].save(i)

			if 'photo' in x:
				try:
					i['photo'] = load_image('app/static/load/users', x['photo']) #, 'base64' if 'type_img' not in x else x['type_img']

				#Ошибка загрузки фотографии
				except:
					return '7'

				else:
					db['users'].save(i)

			return '0'

#Закрытие сессии
		elif x['method'] == 'profile.exit':
			#Не все поля заполнены
			if not on(x, ('token',)):
				return '3'

			i = db['tokens'].find_one({'token': x['token']})
			if i:
				db['tokens'].remove(i)
				return '0'

			#? Несуществующий токен
			else:
				return '4'

#Получение категорий
		elif x['method'] == 'categories.gets':
			categories = []
			for i in db['categories'].find().sort('priority', -1): #{"$unwind": "$Applicants"}
				# print('!!!', i)
				# time.sleep(2)
				del i['_id']

				categories.append(i)
			return dumps(categories)

# db['categories'].insert({
# 	'id': 1,
# 	'parent': 0,
# 	'name': 'Раздел 1',
# 	'url': 'art',
# 	'priority': 50,
# })

#Получение статей #сделать выборку полей
		elif x['method'] == 'articles.gets':
			count = x['count'] if 'count' in x else None

			category = None
			if 'category' in x:
				category = [x['category'],]
				for i in db['categories'].find({'parent': x['category']}):
					category.append(i['id'])
				category = {'category': {'$in': category}}

			articles = []
			for i in db['articles'].find(category).sort('priority', -1)[0:count]:
				del i['_id']
				
				articles.append(i)
			return dumps(articles)

# db['articles'].insert({
# 	'id': 1,
# 	'name': 'Title',
# 	'priority': 50,
# 	'cont': 'Text',
# 	'tags': ['article', 'test'],
# 	'description': 'descr',
# 	'author': 1,
# 	'time': 1528238479.252285,
# 	'category': 1,
# 	'status': 3, 1 - черновик 2 - на редакцию 3 - опубликовано 4 - скрыто
# 	'view': [1, 2],
# 	'like': [1,],
# 	'dislike': [2,],
# 	'comment': [],
# })

#Получение статьи
		elif x['method'] == 'articles.get':
			#Не все поля заполнены
			if not on(x, ('id',)):
				return '3'

			i = db['articles'].find_one({'id': x['id']})

			if i:
				del i['_id']
				return dumps(i)

			#Несуществует такой статьи
			else:
				return '4'

#Редактирование статьи
		elif x['method'] == 'articles.edit':
			#Не все поля заполнены
			if not on(x, ('id',)):
				return '3'

			query = db['articles'].find_one({'id': x['id']})

			#Отсутствует такая статья
			if not query:
				return '4'

			if 'name' in x:
				query['name'] = x['name'].strip()
			if 'description' in x:
				query['description'] = x['description'].replace('\r\n', '').replace('\n', '').strip()
			if 'cont' in x:
				query['cont'] = x['cont'].strip()

			query['status'] = 3 #!

			for i in ('category', 'tags', 'priority'):
				if i in x: query[i] = x[i]

			db['articles'].save(query)

			if 'preview' in x:
				files = listdir('app/static/load/articles')
				for i in files:
					if str(x['id']) + '.' in i:
						remove('app/static/load/articles/' + i)

				try:
					load_image('app/static/load/articles', x['preview'], x['id'], x['file'].split('.')[-1] if 'file' in x else None)

				#Ошибка загрузки изображения
				except:
					return '5'

			return '0'

#Добавление статьи
		elif x['method'] == 'articles.add':
			#Не все поля заполнены
			if not on(x, ('name', 'category', 'cont', 'tags', 'description', 'priority')):
				return '3'

			x['name'] = x['name'].strip()
			x['description'] = x['description'].replace('\r\n', '').replace('\n', '').strip()
			x['cont'] = x['cont'].strip()

			try:
				id = db['articles'].find().sort('id', -1)[0]['id'] + 1
			except:
				id = 1

			query = {
				'id': id,
				'author': user,
				'time': time.time(),
				'status': 3, #!
				'view': [user,],
				'like': [],
				'dislike': [],
				'comment': [],
			}

			for i in ('name', 'category', 'cont', 'tags', 'description', 'priority'):
				if i in x: query[i] = x[i]

			db['articles'].insert(query)

			if 'preview' in x:
				try:
					load_image('app/static/load/articles', x['preview'], id, x['file'].split('.')[-1] if 'file' in x else None)

				#Ошибка загрузки изображения
				except:
					return '4'

			return dumps({'id': id})

#Получение пользователя
		elif x['method'] == 'users.get':
			#Не все поля заполнены
			if not on(x, ('id',)) and not on(x, ('login',)):
				return '3'

			i = db['users'].find_one({'id': x['id']} if 'id' in x else {'login': x['login']})

			if i:
				del i['_id']
				return dumps(i)

			#Несуществует такого человека
			else:
				return '4'

#Поиск
		elif x['method'] == 'search':
			pass

#Поиск
		elif x['method'] == 'search':
			pass

#Поиск
		elif x['method'] == 'search':
			pass

		else:
			return '2'

	#Серверная ошибка
	except:
		return '1'