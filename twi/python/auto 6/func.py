import sys, tweepy, time, re
from json import *
from multiprocessing import Process, Manager

#Авторизация
def auth(user=''):
	with open('set.txt', 'r') as file:
		s=loads(file.read())
		if not user: user=s['default']['Me']
		consumer_key, consumer_secret=s['key']['main'] #
		access_key, access_secret=s['key'][user] #

	aut=tweepy.OAuthHandler(consumer_key, consumer_secret)
	aut.set_access_token(access_key, access_secret)
	return tweepy.API(aut)

#Анализ пользователя
def subscribe(i, x, s=[]):
#Поиск топ-пользователей
	if i.followers_count>=0.5*i.friends_count and i.followers_count>=5000:
		with open('set.txt', 'r') as file:
			s=loads(file.read())
		s['top'].append(i.id)
		with open('set.txt', 'w') as file:
			print(dumps(s, ensure_ascii=False, indent=4), file=file)

#Подписка
	elif i.friends_count>=0.6*i.followers_count and not i.follow_request_sent and not i.following and i.screen_name not in s and not x['api'].show_friendship(source_screen_name=i.screen_name, target_screen_name=x['me'])[0].following:
		with open('follow.txt', 'a') as file:
			print(i.screen_name, file=file)
			print('Add follow.', i.screen_name) #
			return True
	return False

#Анализ твита
def post(user, x, follow=False):
	t=True #
	#Обрезаются твиты
	for i in x['api'].user_timeline(user):
#Русский?
		if (x['NotRussian'] or i.lang=='ru') and not i.is_quote_status and not i.in_reply_to_user_id and not i.in_reply_to_status_id and (i.favorite_count>=30 or i.retweet_count>=10):

#Репост
			if follow:
				if t: #Ограничение ретвитов
					x['api'].retweet(i.id)
					print('Repost.', user)
					time.sleep(60)
					t=False #

#Пост
			else:
#Убирает надпись ретвит
				u=re.sub(r'^RT @\w+: ', '', i.text)
#Есть ли обращения?
				if '@' not in u:
					with open('twit.txt', 'a') as file:
						#Замена &amp; &gt;
						print(dumps({'text':u}, ensure_ascii=False), file=file)
					print('Add post.', user) #