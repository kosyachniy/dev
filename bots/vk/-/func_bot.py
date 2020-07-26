import time, requests, vk_api, json
from io import BytesIO #

with open('keys.json', 'r') as file:
	s = json.loads(file.read())

	vk = vk_api.VkApi(token=s['token'])
	vk.auth()

def genCatImage():
	r = requests.get('http://i.stack.imgur.com/bq6O5.png')
	if r.status_code == requests.codes.ok:  # image returned OK
		img = BytesIO(r.content)  # create BytesIO object from the request
		r.close()  # close the get request
		return img  # return the BytesIO object
	else:  # request failed to retrieve the image
		r.close()  # close the get request
		return genCatImage()  # try to return another image

def uploadImage(url, params, file):
	post_params = {'parameters': params}
	files = {'file': file.getvalue()}
	r = requests.post(url, data=post_params, files=files)
	file.close()  # close the BytesIO object




def send(user, cont='', img=[]):
	for i in range(len(img)):
		if img[i][0:5] != 'photo':
#Загружаем фото

			a = vk.method('photos.getMessagesUploadServer')

			if img[i][0:4] == 'http':
				with open('re.jpg', 'wb') as file:
					file.write(requests.get(img[i]).content)
				file = open('re.jpg', 'rb')
			else:
				file = open(img[i], 'rb')
			b = requests.post(a['upload_url'], files={'photo': genCatImage().getvalue()}).json()
			print(b)

			c = vk.method('photos.saveMessagesPhoto', {'photo': b['photo'], 'server': b['server'], 'hash': b['hash']})[0]

			img[i] = 'photo{}_{}'.format(c['owner_id'], c['id'])

	return vk.method('messages.send', {'user_id': user, 'message': cont, 'attachment': ','.join(img)})

read=lambda: [[i['user_id'], i['body']] for i in vk.method('messages.get')['items'] if not i['read_state']][::-1]

dial=lambda: [i['message']['user_id'] for i in vk.method('messages.getDialogs')['items']]

def info(user):
	x=vk.method('users.get', {'user_ids': user, 'fields': 'verified, first_name, last_name, sex, bdate, photo_id, country, city, screen_name'})[0]
	#, lang, phone, timezone, home_town

#Форматируем дату
	bd=x.get('bdate').count('.')
	if bd==2:
		bd=time.strftime('%Y%m%d', time.strptime(x['bdate'], '%d.%m.%Y'))
	elif bd==1:
		bd=time.strftime('%m%d', time.strptime(x['bdate'], '%d.%m'))
	else:
		bd=0

	y=(x.get('verified'), x.get('first_name'), x.get('last_name'), x.get('sex'), int(bd), x.get('photo_id'), str(x.get('country')['id'])+'/'+str(x.get('city')['id']), user, x.get('screen_name'))
	#, 0, 0, 3, 0
	#, x.get('lang'), x.get('phone'), x.get('timezone'), x.get('home_town')
	return tuple(i if i!=None else 0 for i in y)