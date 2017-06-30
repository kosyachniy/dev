from func import *
from json import loads

def new(x):
	it=0
	while True:
		me=x['Me']
		api=auth(me)

		u=x['StartFollow']

		try:
			for i in api.followers():
				#Повторяется
				#Не рассмотрен случай, если последний пользователь удалится / сменит имя
				if i.screen_name==u: break

				user=i.screen_name
				it+=1

#Подписываться на недавно подписавшихся меня ради фолловинга (при каждой подписке)
				if 3*i.followers_count>=i.friends_count>=0.8*i.followers_count>=800 and not i.following and not i.follow_request_sent:
					with open('follow.txt', 'a') as file:
						print(user, file=file)
						print('My follow.', user) #

#Отправлять сообщение
				if x['Message']:
					api.send_direct_message(user, text=x['Message'])
					print('Message. {}.'.format(it), user)
		except tweepy.error.TweepError:
			print('Ошибка новых пользователей!')

#Добавление в БД
		finally:
			time.sleep(60)

		u=user
		time.sleep(300)