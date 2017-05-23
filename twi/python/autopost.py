import requests
from urllib.request import urlopen, unquote
from func import *

get=lambda x: requests.get(x).text

def tag():
	for j in api.trends_place(23424936)[0]['trends']:
		cont=unquote(j['query'].replace('+',' '))
		if '#' in cont:
			return cont
	return api.trends_place(23424936)[0]['trends'][0]

def cont():
	a=tag()
	while True:
		text=get('http://api.forismatic.com/api/1.0/?method=getQuote&format=text&language=ru')+'\n'+a
		if len(text)<=140:
			return text

def post(text):
	if not text:
		text=cont()
	api.update_status(text)
	return text

post('')