import requests, time
from urllib.request import urlopen, unquote
from func import *

name='mashablegif' #lifehacker #iwantyouuur
place=0 #2352824 #23424936

#get=lambda x: requests.get(x).text

def tag():
	for j in api.trends_place(place)[0]['trends']:
		cont=unquote(j['query'].replace('+',' '))
		if '#' in cont:
			return cont
	return api.trends_place(place)[0]['trends'][0]

def lis(user):
	b=list()
	a=tag()
	for i in api.user_timeline(user):
		if not i.retweeted and not i.in_reply_to_user_id and not i.is_quote_status and not i.in_reply_to_user_id and not i.in_reply_to_status_id and i.favorite_count>=5:
			text=i.text+'\n'+a
			if len(text)<=140:
				b.append(text)
	return b

way=lis(name)
while True:
	text=way[0]
	if len(way)==1:
		way+=lis(api.followers(name)[0].screen_name)
	if len(way)==1:
		break
	try:
		api.update_status(text)
		print(text)
		time.sleep(40)
	except tweepy.error.TweepError:
		print('Error')
	del way[0]