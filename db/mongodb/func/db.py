"""
Database
"""

import json

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


with open('sets.json', 'r') as file:
    sets = json.loads(file.read())['mongo']


params = {
    'host': sets['host'],
    'port': 27017,
}

if sets['login'] and sets['password']:
    params['username'] = sets['login']
    params['password'] = sets['password']
    params['authSource'] = 'admin'
    params['authMechanism'] = 'SCRAM-SHA-1'

db = MongoClient(**params)[sets['db']]
