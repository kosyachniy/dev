from func import *

me='deepinmylife'
api=auth(me)
it=0

for i in tweepy.Cursor(api.friends, id=me).items():
	it+=1
	if it%50==0:
		api=auth(me)

	api.destroy_friendship(i.screen_name)
	print('Unfollow. {}.'.format(it),i.screen_name)

	time.sleep(5)