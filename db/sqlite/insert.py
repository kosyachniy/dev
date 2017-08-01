from func import *

db.execute("INSERT INTO note VALUES (1, 'Заголовок', 'Содержание', '01.08.2017 03:01:00')")

auth.commit()
auth.close()