from pymongo import MongoClient

ndb='testdb'
ncoll='testcoll'

'''
client=MongoClient('mongodb://root:asdrqwerty09@invo-shard-00-00-guyjh.mongodb.net:27017,invo-shard-00-01-guyjh.mongodb.net:27017,invo-shard-00-02-guyjh.mongodb.net:27017/INVO?ssl=true&replicaSet=INVO-shard-0&authSource=admin')
db=client.test1
coll=db.test2
'''
db=MongoClient('mongodb://root:asdrqwerty09@invo-shard-00-00-guyjh.mongodb.net:27017,invo-shard-00-01-guyjh.mongodb.net:27017,invo-shard-00-02-guyjh.mongodb.net:27017/INVO?ssl=true&replicaSet=INVO-shard-0&authSource=admin')[ndb]
coll=db[ncoll]
for i in coll.find():
	print(i)
'''
find({_:_}) условия поиска
print(i['_']) какое поле выводить
'''