import time, sys
from func import auth

mess='Привет! Давай знакомиться. Я взаимный)) Подписывайся - https://www.instagram.com/mr.poloz/'

def userr(me='kosyachniy',last=''):
	while True:
		api=auth(me)

		user=list()
		for i in api.followers():
			if i.screen_name==last: #Не рассмотрен случай, если последний пользователь удалится / сменит имя
				break
			user.append(i.screen_name)
		if len(user):
			last=user[0]

			for i in user:
				try:
					api.send_direct_message(i,text=mess)
					print('Message.',i)
				except tweepy.error.TweepError:
					print('Ошибка отправки сообщения!')

				time.sleep(30)

			#Добавление в БД

			#Удаление невзаимных

		time.sleep(600)

if __name__=='__main__':
	if len(sys.argv)==2:
		userr('kosyachniy',sys.argv[1])
	else:
		userr()