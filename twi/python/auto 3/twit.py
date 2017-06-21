from func import *

def post(me=''):
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

			try:
				api.update_status(u)
				print('Post {}.'.format(it),u)
			except tweepy.error.TweepError:
				print('Ошибка при постинге!')

			time.sleep(40)
		else:
			time.sleep(600)

if __name__=='__main__':
	post()