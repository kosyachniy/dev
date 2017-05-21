import sys, os, ssl, chardet
if sys.version_info[0]>=3:
	from urllib.request import urlopen, unquote, Request
else:
	from urllib import urlopen, unquote, Request
from func import *

def get(src):
	with urlopen(Request(src,None,{'User-Agent':''})) as site:
		return site.read().decode('utf-8')

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
	api.update_status(text) #Отправка текстового твита
	return text

if __name__=='__main__':
	post('')