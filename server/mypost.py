import requests

'''
with open('', 'rb') as file:
	files = {'media': file.read()}
'''

cont = requests.post('http://159.65.19.204/',
	json = {
		'cm': 'auth',
		'login': 'Alex',
		'pass': 'Poloz',
	},
	#files = files
)

print(cont.text)