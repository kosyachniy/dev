from pymongo import MongoClient

db = MongoClient()['corpus']
dic = db['dictionary']

alphabet = 'йцукенгшщзхъёфывапролджэячсмитьбюqwertyuiopasdfghjklzxcvbnm- '
texted = lambda x: str([i for i in x if i in alphabet])

read = lambda: input().split(';')

while True:
	num = 0
	for i in dic.find():
		num = max(num, i['id'])
		print(i['id'], i['word'][0][0])

	doc = dic.findone({'id': int(input())})
	if doc:
		print(doc['word'][0], '\n', doc['speak'][0])
		doc['speak'][0].extend(read())
	else:
		doc = {
			'id': num + 1,
			'word': [read()],
			'speak': [read()],
			'sentence': None,
		}
	dic.save(doc)