"""
Database functionality
"""

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from libdev.cfg import cfg


params = {
    'host': cfg('mongo.host'),
    'port': 27017,
}

if cfg('mongo.login') and cfg('mongo.password'):
    params['username'] = cfg('mongo.login')
    params['password'] = cfg('mongo.password')
    params['authSource'] = 'admin'
    params['authMechanism'] = 'SCRAM-SHA-1'

db = MongoClient(**params)[cfg('mongo.db')]


__all__ = (
    'db',
    'DuplicateKeyError',
)
