from func import *

with db:
	db.execute("DELETE FROM note WHERE id=(?)'", (0,))