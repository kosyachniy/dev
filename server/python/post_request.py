import requests

'''
with open('', 'rb') as file:
	files = {'media': file.read()}
'''

link = 'https://tensy.org:5000/'
cont = {
	'method': 'ladders.gets',
	'language': 'ru',
}

cont = requests.post(link, json=cont) #, files = files)
print(cont.text)
