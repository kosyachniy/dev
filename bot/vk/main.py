import vk_api

vk = vk_api.VkApi(login = '79266202893', password = 'odevira18988189B')
#vk_api.VkApi(token = 'a02d...e83fd') #Авторизоваться как сообщество
vk.auth()

def mess(user_id, s):
	vk.method('messages.send', {'user_id':user_id, 'message':s})

mess(140420515, 'хоба работает')