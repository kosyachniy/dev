from func import *
from random import randint

def follow(x):
	me=x['Me']
	api=auth(me)

	it=0
	er=0

	while True:
		s=[i[:-1] for i in open('follow.txt', 'r').readlines()]
		if len(s):
			u=s[0]
			del s[0]
			#open('follow.txt', 'w').write('\n'.join(s))
			with open('follow.txt', 'w') as file:
				for i in s:
					print(i, file=file)

			it+=1
			if it%300==0:
				print('Заснул!')
				time.sleep(20000)

			try:
				api.get_user(u).follow()
				print('Follow {}.'.format(it),u)
				er=0
			except tweepy.error.TweepError:
				print('Ошибка при фолловинге!')

#Контроль длительной ошибки
				er+=1
				if er==10:
					break
				else:
					time.sleep(3**er)
	
			time.sleep(randint(60, 120)) #90
		else:
			time.sleep(600)