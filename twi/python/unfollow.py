from func import *

who='deepinmylife'

def unf(me=''):
	api=auth(me)
	it=0
	while True:
		for i in tweepy.Cursor(api.friends,id=me).items():
#Удаление невзаимных
			#Удаляет с последнего
			if not api.show_friendship(source_screen_name=i.screen_name,target_screen_name=me)[0].following:
				it+=1
				api.destroy_friendship(i.screen_name)
				print('Unfollow. {}.'.format(it),i.screen_name)
				time.sleep(60)
			time.sleep(10)
		time.sleep(400000)

if __name__=='__main__':
	unf(who)