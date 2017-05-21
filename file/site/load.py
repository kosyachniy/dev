import codecs, ssl, chardet
from urllib.request import urlopen, Request

db='db.txt'

def get(src):
	with urlopen(Request(src,None,{'User-Agent':''}),context=ssl._create_unverified_context()) as site:
		with codecs.open(db,'w','utf-8') as file:
			print(site.read().decode('utf-8'),file=file)

if __name__=='__main__':
	get(input())
	print('OK')