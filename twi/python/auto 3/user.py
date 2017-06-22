from func import *

def search(me='', u='', t=True, p=True):
	api=auth(me)
	me=api.me().screen_name
	if not u: u=api.followers()[0].screen_name
	s=list()

	it=0
	while True:
		s=[i[:-1] for i in open('follow.txt', 'r').readlines()]
		if len(s)<200:
			it+=1
			print('Итерация',it)

			for i in api.followers(u):
#Проверка: Русский? Не я?
				if (t or i.lang=='ru') and i.screen_name!=me:

#Поиск пользователей
					if i.friends_count>=0.6*i.followers_count and not i.follow_request_sent and not i.following and i.screen_name not in s and not api.show_friendship(source_screen_name=i.screen_name, target_screen_name=me)[0].following:
						with open('follow.txt', 'a') as file:
							print(i.screen_name, file=file)
							print('Add follow.',i.screen_name)

#Поиск твитов
					if p:
						for j in api.user_timeline(i.screen_name):
							if not j.is_quote_status and not j.in_reply_to_user_id and not j.in_reply_to_status_id and (j.favorite_count>=30 or j.retweet_count>=10):
								#Убирать надпись ретвит
								try:
									api.retweet(j.id)
								except tweepy.error.TweepError:
									print('Ошибка репоста!')
								print('Repost.',i.screen_name)
						time.sleep(60)

			u=s[0] if len(s) else api.followers()[0].screen_name

			'''
		if len(s)<200:
			try:
				lu(u)
			except tweepy.error.TweepError:
				api=auth(me)

		if len(s)==0:
			print('Закончились пользователи!')
			u=api.followers()[i].screen_name
			i=0 if i==19 else i+1
			continue
			'''
			
			time.sleep(60)
		else:
			time.sleep(600)

if __name__=='__main__':
	search(u=sys.argv[1], t=False) if len(sys.argv)==2 else search(t=False)