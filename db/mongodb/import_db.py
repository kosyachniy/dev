"""
Import all project data from backup files to DB
"""

import os
import json

from consys._db import get_db
from libdev.cfg import cfg


db = get_db(
    cfg('mongo.host'),
    cfg('project_name'),
    cfg('mongo.login'),
    cfg('mongo.password'),
)


dbs = [f[:-4] for f in os.listdir('/backup/') if f[-4:] == '.txt']

for db_name in dbs:
    with open(f'/backup/{db_name}.txt', 'r', encoding='utf-8') as file:
        for row in file:
            try:
                db[db_name].insert_one(json.loads(row))
            # pylint: disable=bare-except
            except:
                print(f'❌ {row}')

    print(f'✅\t{db_name}')
