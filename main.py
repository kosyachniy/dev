import sys

def site(url='http://jenyay.net/'):
	sys.path.append('site')
	from open import get
	print(get(url))
def twit(text=''):
	sys.path.append('twi/python')
	from text import post
	print(post(text))

if __name__=='__main__':
#	params=(sys.argv[i] for i in range(2,len(sys.argv)))
#	for i in params: print(i)
	if len(sys.argv)==3:
		globals()[sys.argv[1]](sys.argv[2])
	else:
		globals()[sys.argv[1]]()