from func.db_mongo import db

# Delete all
db.test.remove()

# Delete some
for i in db.test.find({'param': True}):
    db.test.remove(i['_id'])
