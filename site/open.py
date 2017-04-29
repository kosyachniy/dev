import codecs, sys, os, ssl
if sys.version_info[0]>=3:
	from urllib.request import urlretrieve, urlopen
else:
	from urllib import urlretrieve, urlopen

db='db.uple'

def get(src):
	urlretrieve(src,db)
	with codecs.open(db,'r','utf-8') as file:
		return file.read()

print(get(input()))

path=os.path.join(os.path.abspath(os.path.dirname(__file__)),db)
os.remove(path)
