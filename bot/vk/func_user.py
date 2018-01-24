import requests, vk_api, json

with open('keys.txt', 'r') as file:
	s=json.loads(file.read())

	vks=vk_api.VkApi(login=s['login'], password=s['password'])
	vks.auth()

#Загружаем изображение на сервер
			with open('re.jpg', 'wb') as file:
				file.write(requests.get(img[i]).content)

#Загружаем изображение в ВК
			photo=vk_api.VkUpload(vks).photo('re.jpg', group_id=151412216, album_id=247265476)[0]
			img[i]='photo{}_{}'.format(photo['owner_id'], photo['id'])