from codecs import open
import sys, ssl, chardet
if sys.version_info[0]>=3:
	from urllib.request import urlopen
else:
	from urllib import urlopen

def read():
	text=[]
	with open('data.txt','r',encoding='utf-8') as file:
		return file.read()

def write(text):
	with open('data.txt','a',encoding='utf-8') as file:
		print(text,file=file)

def db():
	###

def open(src):
	context=ssl._create_unverified_context()
	with urlopen(src,context=context) as site:
		text=site.read()
		return text.decode(chardet.detect(text)['encoding'])