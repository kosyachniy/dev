from func import db

db=db('testdb')
coll=db['testcollection']
coll.save({'name':'Alex','adr':'S.Petersburg','ball':{'math':'4','prog':(1,2,3,4,5)}})