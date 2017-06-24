from func import *

def search(x):
	api=auth(x['Me'])
	me=api.me().screen_name

	u=x['StartFollow'] if x['StartFollow'] else api.followers()[0].screen_name
	s=list()

	it=0
	while True:
		s=[i[:-1] for i in open('follow.txt', 'r').readlines()]
		if len(s)<200:
			it+=1
			print('Итерация',it) #
			if it%50==0: api=auth(me) #

			for i in api.followers(u):
#Проверка: Русский? Не я?
				if (x['NotRussian'] or i.lang=='ru') and i.screen_name!=me:
					f=subscribe(i, me, s)

					if x['Post']: post(i.screen_name, me, f)
					time.sleep(60) #

			u=s[0] if len(s) else api.followers()[0].screen_name

			time.sleep(60)
		else:
			time.sleep(600)