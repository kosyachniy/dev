char='йцукенгшщзхъёфывапролджэячсмитьбюqwertyuiopasdfghjklzxcvbnm1234567890'

def text(cont):
	cont=list(cont.lower())
	for i in range(len(cont)):
		if cont[i] not in char:
			cont[i]=' '
	return ''.join(cont).split()