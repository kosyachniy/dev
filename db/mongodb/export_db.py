import os
import json
import datetime

from libdev.cfg import cfg
from libdev.time import get_time
from pymongo import MongoClient


params = {
    'host': cfg('mongo.host'),
    'port': 27017,
}

if cfg('mongo.login') and cfg('mongo.password'):
    params['username'] = cfg('mongo.login')
    params['password'] = cfg('mongo.password')
    params['authSource'] = 'admin'
    params['authMechanism'] = 'SCRAM-SHA-1'

db_all = MongoClient(**params)


current_folder = f"backup/{get_time(template='%Y%m%d%H%M%S', tz=3)}"
os.mkdir(current_folder)

for db_name in db_all.list_database_names():
    if db_name in ('admin', 'config', 'local'):
        continue

    print(f"--- {db_name} ---")
    os.mkdir(f"{current_folder}/{db_name}")

    db = db_all[db_name]
    collections = [collection['name'] for collection in db.list_collections()]

    for collection_name in collections:
        print(collection_name, end=" ")

        with open(
            f"{current_folder}/{db_name}/{collection_name}.txt", 'w'
        ) as file:
            for i in db[collection_name].find():
                del i['_id']
                for key in i:
                    if isinstance(i[key], datetime.datetime):
                        i[key] = datetime.datetime.timestamp(i[key])
                print(json.dumps(i, ensure_ascii=False), file=file)

        print("✅")
