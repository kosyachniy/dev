import sys, ssl, chardet
if sys.version_info[0]>=3:
	from urllib.request import urlopen
else:
	from urllib import urlopen

def get(src):
	context=ssl._create_unverified_context()
	with urlopen(src,context=context) as site:
		text=site.read()
		return text.decode(chardet.detect(text)['encoding'])

if __name__=='__main__':
	print(get(input()))