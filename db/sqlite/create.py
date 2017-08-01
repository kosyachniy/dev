from func import *

db.execute("CREATE TABLE note (id int, name text, cont text, time text)")

auth.commit()
auth.close()