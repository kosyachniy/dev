import requests, time
from urllib.request import urlopen, unquote
from func import *

#get=lambda x: requests.get(x).text

def tag():
	for j in api.trends_place(23424936)[0]['trends']:
		cont=unquote(j['query'].replace('+',' '))
		if '#' in cont:
			return cont
	return api.trends_place(23424936)[0]['trends'][0]

def lis(user):
	b=list()
	a=tag()
	for i in api.user_timeline(user):
		if not i.retweeted and not i.in_reply_to_user_id and not i.is_quote_status and not i.in_reply_to_user_id and not i.in_reply_to_status_id and i.favorite_count>=5:
			text=i.text+'\n'+a
			if len(text)<=140:
				b.append(text)
	return b

way=lis('fozkahuckster')
while True:
	if len(way)==0:
		break
	text=way[0]
#	if len(way)<=1:
#		way+=lis(api.followers(name)[0].screen_name)
	try:
		api.update_status(text)
		print(text)
		time.sleep(40)
	except tweepy.error.TweepError:
		print('Error')
	del way[0]