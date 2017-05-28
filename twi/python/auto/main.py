import time, threading
from urllib.request import unquote
from func import auth
from post import 

api=auth()
me=api.me().screen_name

def luser(user):
	a=list()
	for i in api.followers(user):
		name=i.screen_name
		if name!=me and i.friends_count>=0.6*i.followers_count:
			y=api.show_friendship(source_screen_name=name,target_screen_name=me)[0]
			if name not in a and y.following==False and y.followed_by==False:
				a.append(name)
	return a

def user():
	while True:
		print(123)
		time.sleep(5)

#Автопостинг твитов на базе интернета / популярных твитов (твитить 2400 в день)
threading.Thread(target=userr).start()
while True:
	print(456)
	time.sleep(10)

'''
tuser=True
user=api.me().screen_name
i=0
it=0
while True:
	if it%50==0:
		api=auth()
#Подписываться для накрутки, проверка языка (фолловинг 1 раз в минуту, список 1 раз в минуту)
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
			break

	time.sleep(60)
'''
#Подписываться на недавно подписавшихся меня ради фолловинга (при каждой подписке)
'''
	for i in api.followers(me):
		if i.friends_count>=1000 and i.followers_count>=1000 and i.frends_count*0.8>=i.followers_count and not followed_by:
			api.get_user(i.screen_name).follow()
'''
#Удалять тех, кто в течении недели не подписался (1 раз в день)