from func import *

'''
'''

def post(me=''):
	api=auth(me)
	me=api.me().screen_name

	it=0

	while True:
		with open('twit.txt','r') as file:
			u=loads(file.readlines(1)[0][:-1]))
			
		if len(suser):
		it+=1

		try:
			api.update_status(spost[0])
			print('Post {}.'.format(it),spost[0])
		except tweepy.error.TweepError:
			print('Ошибка при постинге!')
		
		del spost[0]

		time.sleep(40)

if __name__=='__main__':
	post()