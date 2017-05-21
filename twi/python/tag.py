from func import *
from urllib.parse import unquote

'''
for i in api.trends_place(23424936):
	for j in i['trends']:
		print(unquote(j['query'].replace('+',' ')))
'''

for j in api.trends_place(23424936)[0]['trends']:
	cont=unquote(j['query'].replace('+',' '))
	if '#' in cont:
		print(cont)

'''
t=True
for i in api.trends_available():
	if t:
		print(i)
		t=False
	elif i['country']=='Russia':
		print(i)
'''