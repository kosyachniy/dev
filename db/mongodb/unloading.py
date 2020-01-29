import json
from pymongo import MongoClient

BASE = 'tg'
COLLECTIONS = ('actions', 'discussions', 'messages')

db = MongoClient(
        username='admin',
        password='asdrqwerty09',
        authSource='admin',
        authMechanism='SCRAM-SHA-1'
)[BASE]

for collection in COLLECTIONS:
        l = []
        for j in db[collection].find():
                del j['_id']
                l.append(j)

        with open('{}-{}.json'.format(BASE, collection), 'w') as file:
                print(json.dumps(l, ensure_ascii=False, indent='\t'), file=file)
