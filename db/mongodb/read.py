from func import db

db=db('testdb')
coll=db['testcollection']
for i in coll.find():
	print(i)
'''
find({_:_}) условия поиска
print(i['_']) какое поле выводить
'''