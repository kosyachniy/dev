from func import *

db.execute("UPDATE note SET name=1, cont=2, time='20170801031400' WHERE id=1")

auth.commit()
auth.close()