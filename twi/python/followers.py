from func import *

who='deepinmylife'
mess='Привет! Давай знакомиться. Я взаимный)) Подписывайся - https://www.instagram.com/mr.poloz/ Также у меня есть для тебя подарок - : http://q32.ru/35378/http://zodzu.com/'

def userr(me='',t=True,last=''):
	it=0
	while True:
		api=auth(me)

		name=''
		for i in api.followers():
			#Повторяется
			name=i.screen_name
			if name==last: 
				break
			#Не рассмотрен случай, если последний пользователь удалится / сменит имя
			it+=1

#Подписываться на недавно подписавшихся меня ради фолловинга (при каждой подписке)
			x=api.get_user(name)
			foling=x.friends_count
			folers=x.followers_count
			if foling>=1000 and folers>=1000 and 3*folers>=foling>=0.8*folers and not x.following and not x.follow_request_sent:
					x.follow()
					print('Follow.',name)

#Отправлять сообщение
			if t:
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
		if sys.argv[2]=='x':
			userr(who,False)
		elif sys.argv[2]=='v':
			userr(who)
		else:
			userr(who,last=sys.argv[1])
	else:
		userr(who)