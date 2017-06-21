from func import *

def search(me='', user='', t=True, p=True):
	api=auth(me)
	me=api.me().screen_name
	if not user: user=api.followers()[0].screen_name
	suser=list()

	def luser():
		for i in api.followers(user):
#Проверка: Русский? Не я?
			print(i.screen_name)
			if (t or i.lang=='ru') and i.screen_name!=me:
				if p:
					with open('twit.txt', 'a') as file:
						for j in api.user_timeline(i.screen_name):
							if not j.is_quote_status and not j.in_reply_to_user_id and not j.in_reply_to_status_id and j.favorite_count>=10:
								print(dumps({'text':j.text}, ensure_ascii=False), file=file)
								print('Add post.',i.screen_name)

				if i.friends_count>=0.6*i.followers_count and not i.follow_request_sent and not i.following and i.screen_name not in suser and not api.show_friendship(source_screen_name=i.screen_name, target_screen_name=me)[0].following:
					with open('follow.txt', 'a') as file:
						#Убирать надпись ретвит 
						print(i.screen_name, file=file)
						print('Add follow.',i.screen_name)
			time.sleep(60)

	it=0
	while True:
		suser=[i[:-1] for i in open('follow.txt', 'r').readlines()]
		if len(suser)<200:
			it+=1
			print('Итерация',it)

			luser()
			user=suser[-1] if len(suser) else api.followers()[0].screen_name

			'''
#Добавление пользователей с каждой итерации до определённого предела
		if len(suser)<200:
			try:
				luser(user)
			except tweepy.error.TweepError:
				api=auth(me)

		if len(suser)==0:
			print('Закончились пользователи!')
			user=api.followers()[i].screen_name
			i=0 if i==19 else i+1
			continue
			'''

			if len(suser)==0: break
			time.sleep(60)
		else:
			time.sleep(600)

if __name__=='__main__':
	search(user=sys.argv[1], t=False) if len(sys.argv)==2 else search(t=False)