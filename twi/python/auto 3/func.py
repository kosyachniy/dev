import sys, tweepy, time
from json import *

#Авторизация
def auth(user=''):
	if user=='deepinmylife' or user=='': user='all'

	with open('set.txt', 'r') as file:
		s=loads(file.read())['key']

		consumer_key, consumer_secret=s['main']
		access_key, access_secret=s[user]

	aut=tweepy.OAuthHandler(consumer_key,consumer_secret)
	aut.set_access_token(access_key,access_secret)
	api=tweepy.API(aut)
	return api

#Подписка
def subscribe(i):
	if i.friends_count>=0.6*i.followers_count and not i.follow_request_sent and not i.following and i.screen_name not in s and not api.show_friendship(source_screen_name=i.screen_name, target_screen_name=me)[0].following:
		with open('follow.txt', 'a') as file:
			print(i.screen_name, file=file)
			print('Add follow.',i.screen_name) #
			return True
	return False

#Твиты
def post(user, follow=False):
	for i in api.user_timeline(user):
		if not i.is_quote_status and not i.in_reply_to_user_id and not i.in_reply_to_status_id and (i.favorite_count>=30 or i.retweet_count>=10):
			if follow:
				try:
					api.retweet(i.id)
					print('Repost.', user)
					time.sleep(60)
				except tweepy.error.TweepError:
					print('Ошибка репоста!')
			else:
				with open('twit.txt', 'a') as file:
					#Убирать надпись ретвит
  					print(dumps({'text':i.text}, ensure_ascii=False), file=file)
  				print('Add post.', user) #