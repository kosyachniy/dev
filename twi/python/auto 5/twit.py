from func import *

def twit(me=''):
	api=auth(me)
	me=api.me().screen_name

	it=0

	while True:
		s=[i[:-1] for i in open('twit.txt', 'r').readlines()]
		if len(s):
			u=loads(s[0])['text']
			del s[0]
			with open('twit.txt', 'w') as file:
				for i in s:
					print(i, file=file)

			it+=1

			with open('set.txt', 'r') as file:
				q=loads(file.read())['trends']
			#Проверка пост - картинка?
			if q['ru'] not in u and len(u)+len(q['ru'])<=138:
				u+='\n'+q['ru']
			if len(u)+len(q['us'])<140:
				u+=' '+q['us']

			try:
				api.update_status(u)
				print('Post {}.'.format(it),u)
			except tweepy.error.TweepError:
				print('Ошибка при постинге!')

			time.sleep(40)
		else:
			time.sleep(600)

if __name__=='__main__': #
	twit() #