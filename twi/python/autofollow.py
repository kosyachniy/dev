from func import *

who='kosyachniy'

def user(me='kosyachniy',start=''):
	api=auth(me)

	def luser(user):
		a=list()
		for i in api.followers(user):
			name=i.screen_name
			if name!=me and i.friends_count>=0.6*i.followers_count:
				y=api.show_friendship(source_screen_name=name,target_screen_name=me)[0]
				if name not in a and y.following==False and y.followed_by==False:
					a.append(name)
		return a

	if not start:
		start=api.followers()[0].screen_name
	suser=luser(start)
	last=me
	i=1 #Так как на индексе 0 - последний подписчик (я)
	it=0

	while True:
		it+=1
		if it%50==0:
			api=auth(me)

		#Добавление пользователей с каждого до определённого предела

		if len(suser)==0:
			try:
				suser+=luser(api.followers(last)[i].screen_name)
			except tweepy.error.TweepError:
				api=auth(me)
		if len(suser)==0:
			print('Закончились пользователи!')
			if i==10:
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