import time, sys
from func import auth

who='deepinmylife'
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
#Подписываться на недавно подписавшихся меня ради фолловинга (при каждой подписке)
				x=api.get_user(i)
				if x.friends_count>=1000 and x.followers_count>=1000 and x.friends_count>=0.8*x.followers_count:
					y=api.show_friendship(source_screen_name=i,target_screen_name=me)[0]
					if not y.followed_by:
						x.follow()
						print('Follow.',i)

#Отправлять сообщение
				try:
					api.send_direct_message(i,text=mess)
					print('Message.',i)
				except tweepy.error.TweepError:
					print('Ошибка отправки сообщения!')

				time.sleep(60)

#Добавление в БД

#Удаление невзаимных

		time.sleep(600)

if __name__=='__main__':
	if len(sys.argv)==2:
		userr(who,sys.argv[1])
	else:
		userr(who)