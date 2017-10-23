#mongod

from pymongo import *
db = MongoClient()['db']
table = db['table']

table.save({'name':'Alex'})
for i in table:
	print(i)