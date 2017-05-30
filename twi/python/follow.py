import tweepy, time
from func import auth

api=auth()

with open('db.txt','r') as file:
	for i in file:
		name=i[0:-1]
		if name:
			try:
				api.get_user(name).follow()
				print(name)
				time.sleep(60)
			except tweepy.error.TweepError:
				print('Ошибка про фолловинге!')