from func import *
from urllib.request import unquote

def trends(x):
	me=x['Me']
	api=auth(me)

	def tag(place):
		for j in api.trends_place(place)[0]['trends']:
			cont=unquote(j['query'].replace('+',' '))
			if '#' in cont: return cont
		return unquote(api.trends_place(place)[0]['trends'][0])

	while True:
#Обновление трендов
		with open('set.txt', 'r') as file:
			s=loads(file.read())
		s['trends']['ru']=tag(23424936)
		s['trends']['us']=tag(2352824)
		with open('set.txt', 'w') as file:
			print(dumps(s, ensure_ascii=False, indent=4), file=file)

#Автоматический поиск интересных постов по трендам и количеству подписок, ретвитов
		#if x['Post']:

		time.sleep(300)