from func import *

def unf(me=''):
	it=0
	while True:
		api=auth(me)
		me=api.me().screen_name

		j=0
		for i in tweepy.Cursor(api.friends,id=me).items():
			j+=1
#Удаление невзаимных
			if j>2000 and not api.show_friendship(source_screen_name=i.screen_name,target_screen_name=me)[0].following:
				it+=1
				api.destroy_friendship(i.screen_name)
				print('Unfollow. {}.'.format(it),i.screen_name)
				time.sleep(5)
			#if j%100==0: time.sleep(60)
		time.sleep(400000)

if __name__=='__main__': #
	unf() #