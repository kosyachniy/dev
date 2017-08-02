from func import *

with db:
	db.execute("CREATE TABLE note (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, cont text, time text)")