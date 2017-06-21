from func import *
from random import randint

def search(me='', t=True, user=''):
	api=auth(me)
	me=api.me().screen_name
	suser=list()

	def luser(one):
		for i in api.followers(one):
#Проверка: Русский? Взаимный? Не добавлен?
			if (t or i.lang=='ru') and i.screen_name!=me and i.friends_count>=0.6*i.followers_count and not i.follow_request_sent and not i.following and i.screen_name not in suser and not api.show_friendship(source_screen_name=i.screen_name,target_screen_name=me)[0].following:
				suser.append(i.screen_name)

	if not user: user=api.followers()[0].screen_name
	i=0
	it=0
	ok=0

	while True:
		time.sleep(randint(90,180)) #90
		it+=1
		if it%300==0:
			print('6 часов начало')
			time.sleep(20000)

#Добавление пользователей с каждой итерации до определённого предела
		if len(suser)<200:
			try:
				luser(user)
			except tweepy.error.TweepError:
				api=auth(me)

		if len(suser)==0:
			print('Закончились пользователи!')
			user=api.followers()[i].screen_name
			i=0 if i==19 else i+1
			continue

		user=suser[0]
		del suser[0]

		try:
			api.get_user(user).follow()
			print('Follow. {}.'.format(it),user)
			ok=0
		except tweepy.error.TweepError:
			print('Ошибка при фолловинге!')

#Контроль длительной ошибки
			ok+=1
			if ok==10:
				break
			else:
				time.sleep(3**ok)

if __name__=='__main__':
	search(t=False, user=sys.argv[1]) if len(sys.argv)==2 else search(t=False)