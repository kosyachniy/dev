from func import *


with db:
	for i in db.execute("SELECT * FROM note"): # WHERE id=1
		print(i)