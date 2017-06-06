from func import *

who='deepinmylife'
mess='Привет! Давай знакомиться. Я взаимный)) Подписывайся - https://www.instagram.com/mr.poloz/'

def new(me='', t=True, user=''):
	it=0
	while True:
		api=auth(me)

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

if __name__=='__main__':
	if len(sys.argv)==2:
		if sys.argv[2]=='x':
			new(who,False)
		elif sys.argv[2]=='v':
			new(who)
		else:
			new(who,user=sys.argv[1])
	else:
		new(who)