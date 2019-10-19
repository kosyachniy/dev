from pymongo import MongoClient


# Локальный сервер

db = MongoClient()['uple']

# Удалённый сервер

import json

with open('keys.json', 'r') as file:
	keys = json.loads(file.read())['mongo']

db = MongoClient(
	username=keys['user'],
	password=keys['password'],
	authSource='admin',
	authMechanism='SCRAM-SHA-1'
)['uple']

# Глобальный сервер

import json

with open('keys.json', 'r') as file:
	keys = json.loads(file.read())

link = 'mongodb://{user}:{password}@{hosts}/{cluster}?ssl=true&replicaSet={cluster}-shard-0&authSource=admin' # [/[database.collection][?options]]' # &retryWrites=true

keys['hosts'] = ','.join(i['host'] + (':{}'.format(i['port']) if 'port' in i else '') for i in keys['hosts'])
req = link.format(**keys)

db = MongoClient(req)['uple']