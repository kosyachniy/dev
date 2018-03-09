import sys, os

def site(url='http://htmlbook.ru/'):
	from file.site.open import get
	print(get(url))

def vk_bot(user=140420515, text='Привет'):
	sys.path.append('bot/vk')
	#os.chdir('bot/vk')

	from func.vk_user import send
	send(user, text)

if __name__=='__main__':
	if len(sys.argv) > 2:
		globals()[sys.argv[1]](*sys.argv[2:])
	else:
		globals()[sys.argv[1]]()