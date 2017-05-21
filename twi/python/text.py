import sys, os, ssl, chardet
if sys.version_info[0]>=3:
	from urllib.request import urlretrieve, urlopen, unquote
else:
	from urllib import urlretrieve, urlopen, unquote
from func import *

adr='http://api.forismatic.com/api/1.0/?method=getQuote&format=text&language=ru'

def get(src):
	with urlopen(src,context=ssl._create_unverified_context()) as site:
		text=site.read()
		return text.decode(chardet.detect(text)['encoding'])

def tag():
	for j in api.trends_place(23424936)[0]['trends']:
		cont=unquote(j['query'].replace('+',' '))
		if '#' in cont:
			return cont
	return api.trends_place(23424936)[0]['trends'][0]

def cont():
	f=True
	while f:
		text=get(adr)+'\n'+tag()
		if len(text)<=140:
			f=False
	return text

def post(text):
	if not text:
		text=cont()
	api.update_status(text) #Отправка текстового твита
	return text

if __name__=='__main__':
	post('')