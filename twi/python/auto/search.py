from func import *

def search(me='', t=True, user=''):
	api=auth(me)
	me=api.me().screen_name
	suser=list()

	def luser():
		for i in api.followers(user):
#Проверка: Русский?
			print(i.screen_name)
			if (t or i.lang=='ru'):
				with open('twit.txt', 'a') as file:
					for j in api.user_timeline(i.screen_name):
						if not j.is_quote_status and not j.in_reply_to_user_id and not j.in_reply_to_status_id and j.favorite_count>=10:
							print(j.text, file=file)
							print('Add post.',i.screen_name)

				if i.screen_name!=me and i.friends_count>=0.6*i.followers_count and not i.follow_request_sent and not i.following and i.screen_name not in suser and not api.show_friendship(source_screen_name=i.screen_name,target_screen_name=me)[0].following:
					with open('follow.txt', 'a') as file:
						print(i.screen_name, file=file)
						print('Add follow.',i.screen_name)
			time.sleep(60)

	it=0
	while True:
		suser=open('follow.txt', 'r').readlines() #sum(1 for i in open('follow.txt', 'r'))
		if len(suser)<200:
			it+=1
			print('Итерация',it)

			if len(suser):
				user=suser[-1]
			else:
				user=api.followers()[0].screen_name
			luser()

			if len(suser)==0:
				break
			time.sleep(60)
		else:
			time.sleep(600)

if __name__=='__main__':
	search(t=False, user=sys.argv[1]) if len(sys.argv)==2 else search(t=False)