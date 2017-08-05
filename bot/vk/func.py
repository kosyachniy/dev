import vk_api, time, json

with open('set.txt', 'r') as file:
	s=json.loads(file.read())
	login=s['login']
	password=s['password']

	vk=vk_api.VkApi(token=s['token'])
	#vk=vk_api.VkApi(login='', password='')

	vk.auth()

def send(user, cont, img=[]):
	vks=vk_api.VkApi(login=login, password=password)
	vks.auth()

	for i in range(img):
		if img[i][0:5]!='photo':
#Загружаем изображение на сервер
			out=open('re.jpg', 'wb')
			out.write(requests.get(img[i]).content)
			out.close()

#Загружаем изображение в ВК
			upload=vk_api.VkUpload(vks)
			photo=upload.photo('re.jpg', album_id=247265476, group_id=151412216)[0]
			img[i]='photo{}_{}'.format(photo['owner_id'], photo['id'])

	return vk.method('messages.send', {'user_id':user, 'message':cont, 'attachment':','.join(img)})

def read():
	cont=[]
	for i in vk.method('messages.get')['items']:
		if not i['read_state']:
			cont.append([i['user_id'], i['body']])
	return cont[::-1]

dial=lambda: [i['message']['user_id'] for i in vk.method('messages.getDialogs')['items']]

def info(user):
	x=vk.method('users.get', {'user_ids': user, 'fields': 'verified, first_name, last_name, sex, bdate, photo_id, country, city, home_town, screen_name'})[0]
	#, lang, phone, timezone

	bd=x.get('bdate').count('.')
	if bd==2:
		bd=time.strftime('%Y%m%d', time.strptime(x['bdate'], '%d.%m.%Y'))
	elif bd==1:
		bd=time.strftime('%m%d', time.strptime(x['bdate'], '%d.%m'))
	else:
		bd=0

	y=(x.get('verified'), x.get('first_name'), x.get('last_name'), x.get('sex'), int(bd), x.get('photo_id'), str(x.get('country')['id'])+'/'+str(x.get('city')['id']), 0, 0, 3, 0, user, x.get('screen_name'))
	return tuple(i if i!='None' else '0' for i in y)