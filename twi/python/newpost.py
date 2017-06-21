from func import *
from urllib.request import unquote

def post(me=''):
	api=auth(me)
	me=api.me().screen_name
	spost=list()

	def tag(place):
		for j in api.trends_place(place)[0]['trends']:
			cont=unquote(j['query'].replace('+',' '))
			if '#' in cont: return cont
		return unquote(api.trends_place(place)[0]['trends'][0])

	def new(user):
		'''
		for i in api.search(tag(23424936)):
			if i.retweet_count>=10 and not i.is_quote_status and not i.in_reply_to_user_id and not i.in_reply_to_status_id:
				spost.append(i.text)
		'''	
		for i in api.user_timeline(user):
			if not i.is_quote_status and not i.in_reply_to_user_id and not i.in_reply_to_status_id and i.favorite_count>=10:
				spost.append(i.text)

	it=0
	while True:
		it+=1

		if len(spost)==0:
			new()

		try:
			#api.update_status(spost[0])
			print('Post. {}.'.format(it),spost[0])
		except tweepy.error.TweepError:
			print('Ошибка при постинге!')


if __name__=='__main__':
	post()