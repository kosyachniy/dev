from pymongo import MongoClient

db = MongoClient()['corpus']
dic = db['dictionary']

for i in dic.find():
	print(i['word'])
