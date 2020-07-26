import sys
import time
import json
from multiprocessing import Process, Manager

import tweepy

# Авторизация
def auth(user=None):
	if not user:
		with open('sets.json', 'r') as file:
			sets = json.loads(file.read())

		user = sets['default']['Me']

	with open('keys.json', 'r') as file:
		keys = json.loads(file.read())

	consumer_key, consumer_secret = keys['consumer_key'], keys['consumer_secret']
	access_key, access_secret = keys['users'][user]['access_key'], keys['users'][user]['access_secret']

	api = tweepy.OAuthHandler(consumer_key, consumer_secret)
	api.set_access_token(access_key, access_secret)

	return tweepy.API(api)

# Анализ пользователя
def subscribe(i, me, s=[]):
	# Заменить глобальными переменными
	api = auth(me)

# Поиск топ-пользователей
	if i.followers_count >= 0.5*i.friends and i.followers_count >= 5000:
		with open('sets.json', 'r') as file:
			sets = json.loads(file.read())

		sets['top'].append(i.id)

		with open('sets.json', 'w') as file:
			print(dumps(s, ensure_ascii=False, indent='\t'), file=file)

# Подписка
	elif i.friends_count>=0.6*i.followers_count and not i.follow_request_sent and not i.following and i.screen_name not in s and not api.show_friendship(source_screen_name=i.screen_name, target_screen_name=me)[0].following:
		with open('follow.txt', 'a') as file:
			print(i.screen_name, file=file)
			print('Add follow.', i.screen_name) #
			return True
	return False

# Анализ твита
def post(user, me, follow=False):
	# Заменить глобальными переменными
	api = auth(me)
	for i in api.user_timeline(user):
		if not i.is_quote_status and not i.in_reply_to_user_id and not i.in_reply_to_status_id and (i.favorite_count >= 30 or i.retweet_count >= 10):

# Репост
			if follow:
				try:
					api.retweet(i.id)
					print('Repost.', user)
					time.sleep(60)
				except tweepy.error.TweepError:
					print('Ошибка репоста!')

# Пост
			else:
				with open('twit.txt', 'a') as file:
					# Убирать надпись ретвит
					print(dumps({'text': i.text}, ensure_ascii=False), file=file)
				print('Add post.', user) #