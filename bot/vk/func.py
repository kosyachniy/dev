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