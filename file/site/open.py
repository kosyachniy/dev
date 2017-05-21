import sys, ssl, chardet
if sys.version_info[0]>=3:
	from urllib.request import urlopen, Request
else:
	from urllib import urlopen, Request

def get(src):
	with urlopen(Request(src,None,{'User-Agent':''}),context=ssl._create_unverified_context()) as site:
		return site.read().decode('utf-8')

if __name__=='__main__':
	print(get(input()))