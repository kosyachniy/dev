import requests, time
from urllib.request import urlopen, unquote
from func import *

def tag():
	for j in api.trends_place(23424936)[0]['trends']:
		cont=unquote(j['query'].replace('+',' '))
		if '#' in cont:
			return cont
	return api.trends_place(23424936)[0]['trends'][0]

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

#Удалять тех, кто в течении недели не подписался

#Автопостинг твитов на базе интернета / популярных твитов


#api.get_user(input()).id