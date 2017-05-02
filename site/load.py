import codecs, sys, ssl, chardet
if sys.version_info[0]>=3:
	from urllib.request import urlopen
else:
	from urllib import urlopen

db='db.txt'

def get(src):
	with urlopen(src,context=ssl._create_unverified_context()) as site:
		text=site.read()
		with codecs.open(db,'w','utf-8') as file:
			print(text.decode(chardet.detect(text)['encoding']),file=file)

if __name__=='__main__':
	get(input())
	print('OK')