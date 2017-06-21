from func import *
from urllib.request import unquote

def trends(me=''):
	api=auth(me)
	me=api.me().screen_name

	def tag(place):
		for j in api.trends_place(place)[0]['trends']:
			cont=unquote(j['query'].replace('+',' '))
			if '#' in cont: return cont
		return unquote(api.trends_place(place)[0]['trends'][0])

	def lpost(user):
		ru=tag(23424936)
		us=tag(2352824)
		for i in api.user_timeline(user):
			if not i.retweeted and not i.is_quote_status and not i.in_reply_to_user_id and not i.in_reply_to_status_id and i.favorite_count>=10:
				if ru in i.text:
					text=i.text+'\n'+us
				else:
					text=i.text+'\n'+ru+' '+us
				#else: #Проверка пост - картинка?
				#	text=b
				if len(text)<=140: spost.append(text)

	#Автоматический поиск интересных постов по трендам и количеству подписок, ретвитов

	