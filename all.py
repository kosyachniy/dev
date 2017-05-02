import sys, ssl, chardet, pymongo, codecs
if sys.version_info[0]>=3:
	from urllib.request import urlopen
else:
	from urllib import urlopen

def read():
	text=[]
	with codecs.open('data.txt','r',encoding='utf-8') as file:
		return file.read()

def write(text):
	with open('data.txt','a',encoding='utf-8') as file:
		print(text,file=file)

def db(name):
	return pymongo.MongoClient('mongodb://root:asdrqwerty09@invo-shard-00-00-guyjh.mongodb.net:27017,invo-shard-00-01-guyjh.mongodb.net:27017,invo-shard-00-02-guyjh.mongodb.net:27017/INVO?ssl=true&replicaSet=INVO-shard-0&authSource=admin')[name]

def open(src):
	context=ssl._create_unverified_context()
	with urlopen(src,context=context) as site:
		text=site.read()
		return text.decode(chardet.detect(text)['encoding'])