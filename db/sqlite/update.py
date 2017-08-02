from func import *
from datetime import datetime

time=datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")

with db:
	db.execute("UPDATE note SET name=1, cont=2, time=(?) WHERE id=1", (time,))