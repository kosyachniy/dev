from func import *

db.execute("CREATE TABLE note (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, cont text, time text)")

auth.commit()
auth.close()