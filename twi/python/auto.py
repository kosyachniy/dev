import time, tweepy
from urllib.request import unquote
from func import auth

who='deepinmylife'
api=auth(who)
me=api.me().screen_name

def tag(place):
	for j in api.trends_place(place)[0]['trends']:
		cont=unquote(j['query'].replace('+',' '))
		if '#' in cont:
			return cont
	return unquote(api.trends_place(place)[0]['trends'][0])

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

def luser(user):
	a=list()
	for i in api.followers(user):
		name=i.screen_name
		if name!=me and i.friends_count>=0.6*i.followers_count:
			y=api.show_friendship(source_screen_name=name,target_screen_name=me)[0]
			if name not in a and y.following==False and y.followed_by==False:
				a.append(name)
	return a

sname=list()
with open('top.txt','r') as file:
	for i in file:
		sname.append(i[0:-1])
spost=lpost(sname[0])
tpost=True

suser=luser(api.followers()[0].screen_name)
tuser=True
user=api.me().screen_name
i=0

it=0
while True:
	it+=1
	if it%50==0:
		api=auth(who)
	print('--- Итерация:',it,'---')
#Автопостинг твитов на базе интернета / популярных твитов (твитить 2400 в день)
	if tpost:
		while len(spost)==0:
			if len(sname)<=1:
				tpost=False
				print('Закончились твиты!')
				break
			else:
				spost+=lpost(sname[1])
				del sname[0]

	if tpost:
		try:
			api.update_status(spost[0])
			print('Post.',sname[0])
		except tweepy.error.TweepError:
			print('Ошибка при постинге!')
		del spost[0]
#Подписываться для накрутки, проверка языка (фолловинг 1 раз в минуту, список 1 раз в минуту)
	if tuser:
		user=suser[0]
		del suser[0]

	if len(suser)==0:
		try:
			suser+=luser(api.followers(user)[i].screen_name)
		except tweepy.error.TweepError:
			api=auth(who)
	if len(suser)==0:
		print('Закончились пользователи!')
		if i==10:
			user=api.me().screen_name
			i=0
		else:
			tuser=False
			i+=1
	else:
		i=0
		tuser=True

	if tuser:
		try:
			api.get_user(user).follow()
			print('Follow.',user)
		except tweepy.error.TweepError:
			print('Ошибка при фолловинге!')
			break

	time.sleep(60)
#Подписываться на недавно подписавшихся меня ради фолловинга (при каждой подписке)
'''
	for i in api.followers(me):
		if i.friends_count>=1000 and i.followers_count>=1000 and i.frends_count*0.8>=i.followers_count and not followed_by:
			api.get_user(i.screen_name).follow()
'''
#Удалять тех, кто в течении недели не подписался (1 раз в день)