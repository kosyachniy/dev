import requests

'''
with open('', 'rb') as file:
	files = {'media': file.read()}
'''

link = 'http://167.99.128.56/'
'''
	'cm': 'auth',
	'login': 'Alex',
	'pass': 'Poloz',
'''
cont = {
	'cm': 'reg',
	'login': 'kosyachniy',
	'pass': 'asdrasdr',
	'mail': 'polozhev@mail.ru',
}

cont = requests.post(link, json=cont) #, files = files)
print(cont.text)