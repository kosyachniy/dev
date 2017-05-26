import requests, time, tweepy
from urllib.request import unquote

def auth(user='deepinmylife'):
	if (user=='deepinmylife'):
		consumer_key='dyLgjQsoCQHxaLSk1baLOCEQe'
		consumer_secret='tEnKUNJhNlj7JYTZ5pesIyFYhqQckqbEn84O7QcfTaYTb5bGTp'
		access_key='3110781773-wiWQkS9564FBEjEb4pzwrPAJdIvtmQFuu4ofblj'
		access_secret='H9u8EQG10XwQIP1vufpVqMZ4NgIpfWPcH0f6FuDq1UKA6'

	aut=tweepy.OAuthHandler(consumer_key,consumer_secret)
	aut.set_access_token(access_key,access_secret)
	api=tweepy.API(aut)
	return api

api=auth()
me=api.me().screen_name

def tag(place):
	for j in api.trends_place(place)[0]['trends']:
		cont=unquote(j['query'].replace('+',' '))
		if '#' in cont:
			return cont
	return api.trends_place(place)[0]['trends'][0]

def lpost(user):
	a=list()
	b=tag(23424936)+' '+tag(2352824)
	for i in api.user_timeline(user):
		if not i.retweeted and not i.in_reply_to_user_id and not i.is_quote_status and not i.in_reply_to_user_id and not i.in_reply_to_status_id and i.favorite_count>=10:
			if i.text:
				text=i.text+'\n'+b
			else:
				text=b
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

#api.get_user(input()).id

sname=list()
with open('top.txt','r') as file:
	for i in file:
		sname.append(i[0:-1])

suser=luser(api.followers()[0].screen_name)
spost=lpost(sname[0])
del sname[0]
tpost=True
tuser=True
user=api.me().screen_name
i=0
while True:
#Автопостинг твитов на базе интернета / популярных твитов
	if tpost:
		while len(spost)==0:
			if len(sname)==0:
				tpost=False
				print('Твиты закончились!')
			else:
				spost+=lpost(sname[0])
				del sname[0]

		try:
			api.update_status(spost[0])
			print(spost[0])
		except tweepy.error.TweepError:
			print('Ошибка при постинге!')
		del spost[0]
#Подписываться для накрутки, проверка языка
	if tuser:
		user=suser[0]
		del suser[0]
	if len(suser)==0:
		suser+=luser(api.followers(user)[i].screen_name)
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
			print(user)
		except tweepy.error.TweepError:
			print('Ошибка при фолловинге!')
			api=auth()

	time.sleep(60)