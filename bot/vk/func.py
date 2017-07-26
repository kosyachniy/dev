import vk_api, time

vk=vk_api.VkApi(login='', password='')
#vk=vk_api.VkApi(token='')
vk.auth()

send=lambda user, cont: vk.method('messages.send', {'user_id':user, 'message':cont})

def read():
	cont=[]
	for i in vk.method('messages.get')['items']:
		if not i['read_state']:
			cont.append([i['user_id'], i['body']])
	return cont[::-1]

dial=lambda: [i['message']['user_id'] for i in vk.method('messages.getDialogs')['items']]
