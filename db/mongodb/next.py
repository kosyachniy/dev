from func.db_mongo import *

# Индекс следующего элемента
try:
	id = db['test'].find().sort('id', -1)[0]['id'] + 1
except:
	id = 1

print(id)