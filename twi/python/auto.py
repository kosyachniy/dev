

#Подписываться для накрутки, проверка языка

#Подписываться на недавно подписавшихся меня ради фолловинга
'''
for i in api.followers('kosyachniy'):
	if i.friends_count>=1000 and i.followers_count>=1000:
		user=i.screen_name
		break
if not user:
	user=api.followers('kosyachniy')[0].screen_name
'''

#Автопостинг твитов на базе интернета / популярных твитов


#api.get_user(input()).id