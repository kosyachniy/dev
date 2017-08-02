from func import *

db.execute("SELECT * FROM note")
for i in db.fetchall():
	print(i)

'''
db.execute("SELECT * FROM note WHERE id=1")
print(db.fetchone())
'''

auth.commit()
auth.close()