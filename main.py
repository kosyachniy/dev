import sys

def site(url='http://jenyay.net/'):
	sys.path.append('site')
	from open import get
	print(get(url))

if __name__=='__main__':
	t=False;
	for i in sys.argv:
		if t:
			globals()[i]()
		else:
			t=True;
