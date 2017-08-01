import sqlite3

auth=sqlite3.connect('1.db')
db=auth.cursor()

db.execute("SELECT * FROM stocks WHERE id=1")
print(db.fetchone())

auth.commit()
auth.close()