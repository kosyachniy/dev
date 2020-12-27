import os
import json

from pymongo import MongoClient


with open('keys.json', 'r') as file:
	keys = json.loads(file.read())


db_all = MongoClient(
	username=keys['user'],
	password=keys['password'],
	authSource='admin',
	authMechanism='SCRAM-SHA-1'
)

for db_name in os.listdir('db/'):
	if db_name not in ('.', '..'):
		try:
			files = os.listdir('db/{}'.format(db_name))
		except:
			continue

		print('---', db_name, '---')

		db = db_all[db_name]

		for file_name in files:
			collection_name = file_name[:-4]
			print('{}'.format(collection_name), end=' ')

			with open('db/{}/{}'.format(db_name, file_name), 'r') as file:
				for el in file:
					db[collection_name].insert_one(json.loads(el))

			print('✅')