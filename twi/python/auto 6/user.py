from func import *

def search(x):
	u=x['StartFollow'] if x['StartFollow'] else x['api'].followers()[0].screen_name
	s=list()

	it=0 #
	while True:
		s=[i[:-1] for i in open('follow.txt', 'r').readlines()]
		if len(s)<200:
			it+=1 #
			print('Итерация',it,'| подписаться:',len(s)) #

			try:
				for i in x['api'].followers(u):
#Проверка: Русский? Не я?
					if (x['NotRussian'] or i.lang=='ru') and i.screen_name!=x['me']:
						f=subscribe(i, x['me'], s)
						if x['Post']: post(i.screen_name, x['me'], x['NotRussian'], f)
						time.sleep(60) #

				u=s[0] if len(s) else x['api'].followers()[0].screen_name
			except tweepy.error.TweepError:
				x['api']=auth(x['me']) #
				print('Ошибка поиска!')

			time.sleep(60)
		else:
			time.sleep(600)