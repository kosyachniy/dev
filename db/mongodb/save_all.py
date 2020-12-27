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

for db_name in db_all.list_database_names():
	if db_name in ('admin', 'config', 'local'):
		continue

	print('---', db_name, '---')
	os.mkdir('db/{}'.format(db_name))

	db = db_all[db_name]
	collections = [collection['name'] for collection in db.list_collections()]

	for collection_name in collections:
		print('{}'.format(collection_name), end=' ')

		with open('db/{}/{}.txt'.format(db_name, collection_name), 'w') as file:
			for i in db[collection_name].find():
				del i['_id']
				print(json.dumps(i, ensure_ascii=False), file=file) # , indent='\t'

		print('✅')
