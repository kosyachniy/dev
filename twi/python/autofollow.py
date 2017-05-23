from func import *
import time

me=api.me().screen_name

def lis(user):
	a=list()
	for i in api.followers(user):
		name=i.screen_name
		if name!=me and i.friends_count>=0.6*i.followers_count:
			y=api.show_friendship(source_screen_name=name,target_screen_name=me)[0]
			if name not in a and y.following==False and y.followed_by==False:
				a.append(name)
	return a

way=lis(api.followers()[0].screen_name)
while True:
	name=way[0]
	if len(way)<=1:
		way+=lis(api.followers(name)[0].screen_name)
	try:
		api.get_user(name).follow()
		print(name)
	except tweepy.error.TweepError:
		print('Error')
	del way[0]
	time.sleep(60)