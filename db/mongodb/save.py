from json import dumps

from func.mongodb import db


dbs = [collection['name'] for collection in db.list_collections()]

for db_name in dbs:
	with open('db/{}.txt'.format(db_name), 'w') as file:
		for i in db[db_name].find():
			del i['_id']
			print(dumps(i, ensure_ascii=False), file=file) # , indent='\t'

	print('✅\t{}'.format(db_name))