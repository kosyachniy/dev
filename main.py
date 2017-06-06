import sys

def site(url='http://jenyay.net/'):
	from file.site.open import get
	print(get(url))

if __name__=='__main__':
	if len(sys.argv)==3:
		globals()[sys.argv[1]](sys.argv[2])
	else:
		globals()[sys.argv[1]]()