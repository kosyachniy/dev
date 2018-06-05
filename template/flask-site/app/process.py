from flask import request
from app import app

import time, base64
from mongodb import *
from re import findall, match
from hashlib import md5
from json import dumps
from random import randint
from os import listdir

#! если удалить пользователя - новый возможно будет с заниженным id и нарушатся связи в бд

generate = lambda length=32: ''.join([chr(randint(48, 123)) for i in range(length)])
on = lambda x, y: all([i in x for i in y])

def max_image(url):
	x = listdir(url)
	k = 0
	for i in x:
		if '.jpg' in i:
			j = int(i.split('.')[0])
			if j > k:
				k = j
	return k+1

def load_image(url, data, type='base64'):
	if type == 'base64':
		data = base64.b64decode(data)

	id = max_image(url)
	with open(url+'/%d.jpg' % id, 'wb') as file:
		file.write(data)
	return id


@app.route('/', methods=['POST'])
def process():
	x = request.json
	#print(x)

	if 'cm' not in x:
		return '2'

	#Убираем лишние отступы
	for i in x:
		if type(x[i]) == str:
			x[i] = x[i].strip()

	#Определение пользователя
	if 'token' in x:
		user = db['tokens'].find_one({'token': x['token']})['id']
	else:
		user = None

	try:
#Регистрация
		if x['cm'] == 'profile.reg':
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

			return token

#Авторизация
		elif x['cm'] == 'profile.auth':
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

			return token

#Изменение личной информации
		elif x['cm'] == 'profile.settings':
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
		elif x['cm'] == 'profile.exit':
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

#Добавление соревнований
		elif x['cm'] == 'competions.add':
			#Не все поля заполнены
			if not on(x, ('name',)):
				return '3'

			try:
				id = db['competions'].find().sort('id', -1)[0]['id'] + 1
			except:
				id = 1

			if 'owners' in x: del x['owners']
			if user: x['owners'] = [user,]

			query = {'id': id}
			for i in ('name', 'description', 'cont', 'time', 'durability', 'author', 'quantity', 'type', 'prize', 'url', 'geo', 'stage', 'owners'):
				if i in x: query[i] = x[i]

			query['show'] = 0
			db['competions'].insert(query)

			if 'images' in x:
				images = []

				for i in x['images']:
					try:
						image = load_image('app/static/load/competions', i)

					#Ошибка загрузки изображения
					except:
						return '4'

					else:
						images.append(image)

				query = db['competions'].find_one({'id': id}) #оптимизировать
				query['images'] = images
				db['competions'].save(query)

			return 'id%d' % id

#Изменение соревнования
		elif x['cm'] == 'competions.edit':
			#Не все поля заполнены
			if not on(x, ('token', 'id')):
				return '3'

			i = db['tokens'].find_one({'token': x['token']})
			if i:
				id = i['id']

				i = db['users'].find_one({'id': id})
				admin = i['admin'] if 'admin' in i else 0

			#Несуществует токен
			else:
				return '4'

			query = db['competions'].find_one({'id': x['id']})
			if query:
				owners = query['owners']

			#Несуществующий конкурс
			else:
				return '5'

			#Нет прав на редактирование соревнования
			if not admin and id not in owners:
				return '6'

			#Отображение соревнования в списке
			if not query['show'] and 'show' in x and x['show'] and admin < 2:
				return '8'

			for i in ('name', 'description', 'cont', 'time', 'durability', 'author', 'quantity', 'type', 'prize', 'url', 'geo', 'stage', 'show', 'owners'):
				if i in x: query[i] = x[i]
			db['competions'].save(query)

			if 'images' in x:
				images = []

				for i in x['images']:
					if type(i) != int:
						try:
							image = load_image('app/static/load/competions', i)

						#Ошибка загрузки изображения
						except:
							return '7'

						else:
							images.append(image)

					else:
						images.append(i)

				query['images'] = images
				db['competions'].save(query)

			return '0'

#Получить соревнования
		elif x['cm'] == 'competions.gets':
			num = x['num'] if 'num' in x else None

			competions = []
			for i in db['competions'].find().sort('id', -1)[0:num]:
				if 'owners' in i: del i['owners'] #! добавить индикатор есть-нет право на редактирование
				del i['_id']

				competions.append(i)
			return dumps(competions)

#Получить соревнование
		elif x['cm'] == 'competions.get':
			#Не все поля заполнены
			if not on(x, ('id',)):
				return '3'


			x = db['competions'].find_one({'id': x['id']})

			x['access'] = False
			if user:
				query = db['users'].find_one({'id': user})
				if query and 'admin' in query and query['admin'] > 1:
					x['access'] = True

			del x['_id']
			if 'owners' in x:
				if user in x['owners']:
					x['access'] = True
				del x['owners']
			return dumps(x)

#Список пользователей
		elif x['cm'] == 'participants.gets':
			num = x['num'] if 'num' in x else None

			participants = []
			for i in db['users'].find({'rating': {'$exists': True}}).sort('id', -1)[0:num]:
				del i['password']
				del i['_id']
				del i['mail']
				if 'description' in i: del i['description']

				participants.append(i)
			return dumps(participants)

#Получить участника
		elif x['cm'] == 'participants.get':
			#Не все поля заполнены
			if not on(x, ('id',)) and not on(x, ('login',)) and not user:
				return '3'

			if 'id' in x:
				query = db['users'].find_one({'id': x['id']})
			elif 'login' in x:
				query = db['users'].find_one({'login': x['login']})
			else:
				query = db['users'].find_one({'id': user})

			if 'admin' in query: del query['admin']
			del query['password']
			del query['_id']

			return dumps(query)

#Получить новости
		elif x['cm'] == 'news.gets':
			pass

#Получить новость
		elif x['cm'] == 'news.get':
			pass

#Поиск
		elif x['cm'] == 'search':
			pass

		else:
			return '2'

	#Серверная ошибка
	except:
		return '1'