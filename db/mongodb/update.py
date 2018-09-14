from func.db_mongo import *

el = db['test'].find_one({'id': 1})
el['param 1'] = 'me'
db['test'].save(el)