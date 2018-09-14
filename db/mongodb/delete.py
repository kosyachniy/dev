from func.db_mongo import *

# Удалить всё
db['test'].remove()

# Удалить некоторые
for i in db['test'].find({'param': True}):
	db['test'].remove(i['_id'])