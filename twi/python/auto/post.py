import time
from urllib.request import unquote
from func import auth

api=auth()

def tag(place):
	for j in api.trends_place(place)[0]['trends']:
		cont=unquote(j['query'].replace('+',' '))
		if '#' in cont:
			return cont
	return api.trends_place(place)[0]['trends'][0]

def lpost(user):
	a=list()
	ru=tag(23424936)
	us=tag(2352824)
	for i in api.user_timeline(user):
		if not i.retweeted and not i.in_reply_to_user_id and not i.is_quote_status and not i.in_reply_to_user_id and not i.in_reply_to_status_id and i.favorite_count>=10:
			if ru in i.text:
				text=i.text+'\n'+us
			else:
				text=i.text+'\n'+ru+' '+us
			#else: #Проверка пост - картинка?
			#	text=b
			if len(text)<=140:
				a.append(text)
	return a

sname=list()
with open('top.txt','r') as file:
	for i in file:
		sname.append(i[0:-1])

spost=lpost(sname[0])
del sname[0]
tpost=True
while True:
	if tpost:
		while len(spost)==0:
			if len(sname)==0:
				tpost=False
				print('Закончились твиты!')
				break
			else:
				spost+=lpost(sname[0])
				del sname[0]

	if tpost:
		try:
			api.update_status(spost[0])
			print(spost[0])
		except tweepy.error.TweepError:
			print('Ошибка при постинге!')
		del spost[0]