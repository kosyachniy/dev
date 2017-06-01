import sys, tweepy, time
from func import auth

who='deepinmylife'
mess='Привет! Давай знакомиться. Я взаимный)) Подписывайся - https://www.instagram.com/mr.poloz/'

def userr(me='kosyachniy',last=''):
	it=0
	while True:
		api=auth(me)

		name=''
		for i in api.followers():
			name=i.screen_name
			if name==last: 
				break
			#Не рассмотрен случай, если последний пользователь удалится / сменит имя
			it+=1

#Подписываться на недавно подписавшихся меня ради фолловинга (при каждой подписке)
			x=api.get_user(name)
			if x.friends_count>=1000 and x.followers_count>=1000 and x.friends_count>=0.8*x.followers_count:
				y=api.show_friendship(source_screen_name=name,target_screen_name=me)[0]
				if not y.followed_by:
					x.follow()
					print('Follow.',name)

#Отправлять сообщение
			try:
				api.send_direct_message(name,text=mess)
				print('Message. {}.'.format(it),name)
			except tweepy.error.TweepError:
				print('Ошибка отправки сообщения!')

#Добавление в БД

			time.sleep(60)
		last=name
		time.sleep(300)

if __name__=='__main__':
	if len(sys.argv)==2:
		userr(who,sys.argv[1])
	else:
		userr(who)