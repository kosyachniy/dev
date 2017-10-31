import codecs, ssl, chardet
from urllib.request import urlopen, Request

db = 'db.txt'

def get(src):
	with urlopen(Request(src, None, {'User-Agent': ''}), context=ssl._create_unverified_context()) as site:
		text = site.read()
		with codecs.open(db, 'w', 'utf-8') as file:
			print(text.decode(chardet.detect(text)['encoding']), file=file)

if __name__ == '__main__':
	get(input())
	print('OK')