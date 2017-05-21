import sys, os, ssl, chardet
if sys.version_info[0]>=3:
	from urllib.request import urlretrieve, urlopen
else:
	from urllib import urlretrieve, urlopen
from func import *

url='http://t30p.ru/'
adr='http://api.forismatic.com/api/1.0/?method=getQuote&format=text&language=ru'
contain='Тренды твиттера'
start='#'
stop='<'
indent=20

def get(src):
	with urlopen(src,context=ssl._create_unverified_context()) as site:
		text=site.read()
		return text.decode(chardet.detect(text)['encoding'])

def tag():
	text=get(url)
	text=text[text.find(contain)+indent:]
	text=text[text.find(start)+1:]
	return text[:text.find(stop)]

def cont():
	f=True
	a=tag()
	while f:
		text=get(adr)+'\n#'+a
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