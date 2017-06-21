from func import *
from random import randint

def follow(me=''):
	api=auth(me)
	me=api.me().screen_name

	suser=list()
	it=0
	ok=0

	while True:
		if len(suser)==0:
			suser=[i[:-1] for i in open('follow.txt', 'r').readlines()]

		if len(suser):
			it+=1
			if it%300==0:
				print('6 часов начало')
				time.sleep(20000)

			try:
				api.get_user(user).follow()
				print('Follow {}.'.format(it),suser[0])
				ok=0
			except tweepy.error.TweepError:
				print('Ошибка при фолловинге!')

#Контроль длительной ошибки
				ok+=1
				if ok==10:
					break
				else:
					time.sleep(3**ok)

			#Заменить
			del suser[0]
			f1=open('follow.txt', 'r').readlines()
			for i in [0,0,-1]:
				f1.pop(i)
			with open('follow.txt', 'w') as f2:
				f2.writelines(f1)
	
			time.sleep(randint(90,180)) #90
		else:
			time.sleep(600)

if __name__=='__main__':
	follow()