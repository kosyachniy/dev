import time
from func import auth

api=auth()
me=api.me().screen_name

def luser(user):
	a=list()
	for i in api.followers(user):
		name=i.screen_name
		if name!=me and i.friends_count>=0.6*i.followers_count:
			y=api.show_friendship(source_screen_name=name,target_screen_name=me)[0]
			if name not in a and y.following==False and y.followed_by==False:
				a.append(name)
	return a

def user():
	tuser=True
	user=api.me().screen_name
	i=0
	it=0

	while True:
		it+=1
		if it%50==0:
			api=auth()

		if tuser:
			user=suser[0]
			del suser[0]

		if len(suser)==0:
			suser+=luser(api.followers(user)[i].screen_name)
		if len(suser)==0:
			print('Закончились пользователи!')
			if i==10:
				user=api.me().screen_name
				i=0
			else:
				tuser=False
				i+=1
		else:
			i=0
			tuser=True

		if tuser:
			try:
				api.get_user(user).follow()
				print('Follow.',it,'.',user)
			except tweepy.error.TweepError:
				print('Ошибка при фолловинге!')
				break

		time.sleep(60)

if __name__=='__main__':
	user()