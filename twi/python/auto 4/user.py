from func import *

def search(me=''):
	api=auth(me)
	me=api.me().screen_name
	if not u: u=api.followers()[0].screen_name
	s=list()

	while True:
		s=[i[:-1] for i in open('follow.txt', 'r').readlines()]
		if len(s)<200:

			for i in api.followers(u):
				if (t or i.lang=='ru') and i.screen_name!=me:

#Поиск пользователей
					if i.friends_count>=0.6*i.followers_count and not i.follow_request_sent and not i.following and i.screen_name not in s and not api.show_friendship(source_screen_name=i.screen_name, target_screen_name=me)[0].following:
						with open('follow.txt', 'a') as file:
							print(i.screen_name, file=file)

#Поиск твитов
					if p:
						for j in api.user_timeline(i.screen_name):
							if not j.is_quote_status and not j.in_reply_to_user_id and not j.in_reply_to_status_id and (j.favorite_count>=30 or j.retweet_count>=10):
								try:
									api.retweet(j.id)
								except tweepy.error.TweepError:
									print('Error!')
						time.sleep(60)

			u=s[0] if len(s) else api.followers()[0].screen_name
			
			#Умная система поиска пользователей, если их нет

			time.sleep(60)
		else:
			time.sleep(600)