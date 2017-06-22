from func import *
from random import randint

def follow(me=''):
	api=auth(me)
	me=api.me().screen_name

	for it in range(1,300):
		s=[i[:-1] for i in open('follow.txt', 'r').readlines()]
		if len(s):
			u=s[0]
			del s[0]
			with open('follow.txt', 'w') as file:
				for i in s:
					print(i, file=file)

			try:
				api.get_user(u).follow()
				print('Follow.',u)
			except tweepy.error.TweepError:
				print('Ошибка при фолловинге!')
	
			time.sleep(randint(90,180))
		else:
			time.sleep(600)

if __name__=='__main__':
	follow()