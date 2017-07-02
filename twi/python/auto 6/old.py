from func import *

def unf(x):
	it=0
	while True:
		j=0
		for i in tweepy.Cursor(x['api'].friends, id=x['me']).items():
			j+=1
#Удаление невзаимных
			if j>2000 and not x['api'].show_friendship(source_screen_name=i.screen_name,target_screen_name=x['me'])[0].following:
				it+=1
				x['api'].destroy_friendship(i.screen_name)
				print('Unfollow. {}.'.format(it),i.screen_name)
				time.sleep(5)
			#if j%100==0: time.sleep(60)
		time.sleep(400000)