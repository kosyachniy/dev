from func import *

who='kosyachniy'

def user(me='',t=True,start=''):
	api=auth(me)

	def luser(user):
		a=list()
		for i in api.followers(user):
			#Проверка русский ли
			if (t or i.lang=='ru') and i.screen_name!=me and i.friends_count>=0.6*i.followers_count and not i.follow_request_sent and not i.following and not api.show_friendship(source_screen_name=i.screen_name,target_screen_name=me)[0].following:
				a.append(i.screen_name)
		return a

	if not start:
		start=api.followers()[0].screen_name
	suser=luser(start)

	def add(user=me,i=1): #Так как на индексе 0 - последний подписчик (я)
		try:
			suser+=luser(api.followers(user)[i].screen_name)
		except tweepy.error.TweepError:
			api=auth(me)

	last=me
	i=1
	it=0

	while True:
		it+=1
		if it%50==0:
			api=auth(me)

		#Добавление пользователей с каждого до определённого предела
		if len(suser)<=200:
			add(last)

		if len(suser)==0:
			print('Закончились пользователи!')
			if i==10:
				if last==me:
					#Сделать автозапуск при новых пользователях или прошествии большого времени
					break
				else:
					last=me
					i=0
					continue
			else:
				i+=1
				continue
		else:
			i=1

		last=suser[0]
		del suser[0]

		try:
			api.get_user(last).follow()
			print('Follow. {}.'.format(it),last)
		except tweepy.error.TweepError:
			print('Ошибка при фолловинге!')
			#Контроль длительной ошибки

		time.sleep(90)

if __name__=='__main__':
	if len(sys.argv)==2:
		user(who,sys.argv[1])
	else:
		user(who)