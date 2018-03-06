import time, requests, vk_api, json

with open('keys.txt', 'r') as file:
	s = json.loads(file.read())

	vk = vk_api.VkApi(login=s['login'], password=s['password'])
	vk.auth()

def send(user, cont, img=[]):
	for i in range(len(img)):
		if img[i][0:5] != 'photo':
#Загружаем изображение на сервер
			with open('re.jpg', 'wb') as file:
				file.write(requests.get(img[i]).content)

#Загружаем изображение в ВК
			photo = vk_api.VkUpload(vk).photo('re.jpg', group_id=151412216, album_id=247265476)[0]
			img[i] = 'photo{}_{}'.format(photo['owner_id'], photo['id'])

	return vk.method('messages.send', {'user_id':user, 'message':cont, 'attachment':','.join(img)})

read = lambda: [[i['user_id'], i['body']] for i in vk.method('messages.get')['items'] if not i['read_state']][::-1]

dial = lambda: [i['message']['user_id'] for i in vk.method('messages.getDialogs')['items']]

def info(user):
	x = vk.method('users.get', {'user_ids': user, 'fields': 'verified, first_name, last_name, sex, bdate, photo_id, country, city, screen_name, lang, phone, timezone, home_town'})[0]

#Форматируем дату
	try:
		bd = x.get('bdate').count('.')
	except:
		bd = 0

	if bd == 2:
		bd = time.strftime('%Y%m%d', time.strptime(x['bdate'], '%d.%m.%Y'))
	elif bd == 1:
		bd = time.strftime('%m%d', time.strptime(x['bdate'], '%d.%m'))
	else:
		bd = 0

	y = (
		x.get('verified'),
		x.get('first_name'),
		x.get('last_name'),
		x.get('sex'),
		int(bd),
		x.get('photo_id'),
		(str(x.get('country')['id']) if x.get('country') else '0') + '/' + (str(x.get('city')['id']) if x.get('city') else '0'),
		user,
		x.get('screen_name'),
		x.get('lang'), #0
		x.get('phone'), #0
		x.get('timezone'), #3
		x.get('home_town'), #0
	)

	return tuple(i if i != None else 0 for i in y)