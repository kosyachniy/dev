from pymongo import MongoClient

ndb='testdb'
ncoll='testcoll'

db=MongoClient('mongodb://root:asdrqwerty09@invo-shard-00-00-guyjh.mongodb.net:27017,invo-shard-00-01-guyjh.mongodb.net:27017,invo-shard-00-02-guyjh.mongodb.net:27017/INVO?ssl=true&replicaSet=INVO-shard-0&authSource=admin')[ndb]
coll=db[ncoll]
doc={'name':'Alex','adr':'S.Petersburg','ball':{'math':'4','prog':(1,2,3,4,5)}}
coll.save(doc)