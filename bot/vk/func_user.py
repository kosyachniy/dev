import requests, vk_api, json

with open('set.txt', 'r') as file:
	s=json.loads(file.read())

	vks=vk_api.VkApi(login=s['login'], password=s['password'])
	vks.auth()

