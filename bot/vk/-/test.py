import vk_api, time, json

with open('set.txt', 'r') as file:
	vk=vk_api.VkApi(token=json.loads(file.read())['token'])
	#vk=vk_api.VkApi(login='', password='')
vk.auth()

def info(user):
	x=vk.method('users.get', {'user_ids': user, 'fields': 'home_town'})[0]
	return x.get('home_town')

print(info(140420515))