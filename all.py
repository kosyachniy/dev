import sys, ssl, chardet, pymongo, codecs
if sys.version_info[0]>=3:
	from urllib.request import urlopen, Request
else:
	from urllib import urlopen, Request

def read(name='db.txt'):
	text=[]
	with codecs.open(name,'r',encoding='utf-8') as file:
		return file.read()

def write(text,name='db.txt'):
	with open(name,'a',encoding='utf-8') as file:
		print(text,file=file)

def db(name):
	return pymongo.MongoClient('mongodb://root:asdrqwerty09@invo-shard-00-00-guyjh.mongodb.net:27017,invo-shard-00-01-guyjh.mongodb.net:27017,invo-shard-00-02-guyjh.mongodb.net:27017/INVO?ssl=true&replicaSet=INVO-shard-0&authSource=admin')[name]

def site(src):
	with urlopen(Request(src,None,{'User-Agent':''}),context=ssl._create_unverified_context()) as site:
		return site.read().decode('utf-8')