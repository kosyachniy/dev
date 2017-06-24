from func import *
from json import loads

def new(x):
	it=0
	while True:
		me=x['Me']
		api=auth(me)

		#Заменить глобальными переменными
		with open('set.txt', 'r') as file:
			s=loads(file.read())['default']

		mess=s['Message']
		u=s['StartFollow']
		t=s['NotRussian']
		p=s['Post']

		for i in api.followers():
			#Повторяется
			#Не рассмотрен случай, если последний пользователь удалится / сменит имя
			if i.screen_name==user: break

			user=i.screen_name
			it+=1

#Подписываться на недавно подписавшихся меня ради фолловинга (при каждой подписке)
			foling=i.friends_count
			folers=i.followers_count
			if foling>=1000 and folers>=1000 and 3*folers>=foling>=0.8*folers and not i.following and not i.follow_request_sent:
					i.follow()
					print('Follow.',user)

#Отправлять сообщение
			if t:
				try:
					api.send_direct_message(user,text=mess)
					print('Message. {}.'.format(it),user)
				except tweepy.error.TweepError:
					print('Ошибка отправки сообщения!')

#Добавление в БД

			time.sleep(60)
		time.sleep(300)