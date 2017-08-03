import vk_api, time, json

with open('set.txt', 'r') as file:
	vk=vk_api.VkApi(token=json.loads(file.read())['token'])
	#vk=vk_api.VkApi(login='', password='')
vk.auth()

send=lambda user, cont, img=[]: vk.method('messages.send', {'user_id':user, 'message':cont, 'attachment':','.join(img)})

def read():
	cont=[]
	for i in vk.method('messages.get')['items']:
		if not i['read_state']:
			cont.append([i['user_id'], i['body']])
	return cont[::-1]

dial=lambda: [i['message']['user_id'] for i in vk.method('messages.getDialogs')['items']]

def info(user):
	x=vk.method('users.get', {'user_ids': user, 'fields': 'verified, first_name, last_name, sex, bdate, photo_id, country, city, lang, phone, timezone, home_town, screen_name'})[0]

	bd=x.get('bdate').count('.')
	if bd==2:
		bd=time.strftime('%Y%m%d', time.strptime(x['bdate'], '%d.%m.%Y'))
	elif bd==1:
		bd=time.strftime('%m%d', time.strptime(x['bdate'], '%d.%m'))
	else:
		bd=0

	y=(x.get('verified'), x.get('first_name'), x.get('last_name'), x.get('sex'), int(bd), x.get('photo_id'), str(x.get('country')['id'])+'/'+str(x.get('city')['id']), 0, 0, 3, 0, user, x.get('screen_name'))
	return tuple(i if i!='None' else '0' for i in y)