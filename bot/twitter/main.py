import tweepy


consumer_key = 'vveAVFha4hTcjUStnOf0hwEwQ'
consumer_secret = 'F8tFzORTE8DzAAYnz5hHxCBRAClPWf4ABhuGn03GHZ5w2QJtbP'
access_token = '4100776272-b1HK52akcdNp4kpWwfHsg8hFnWzbIlcAoKSstqq'
access_token_secret = 'CyRTkHMRrccPpTWRzc8LJM5nPHkp77G7w4djeUsOsEtzJ'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# print([i.list_members for i in api.me().lists()][0])

# Список пользователей в моих списках

alls = set()

for lis in ('list', 'list1'):
	for member in tweepy.Cursor(api.list_members, 'kosyachniy', lis).items():
		alls.add((member.id, member.screen_name))

login_all = [i[1] for i in alls]
print(login_all)

# Список подписок

count = 0

for i in tweepy.Cursor(api.friends, id='kosyachniy').items():
	if i.screen_name not in login_all:
		# Отписка
		api.destroy_friendship(i.screen_name)

		count += 1
	
	if count == 50:
		break