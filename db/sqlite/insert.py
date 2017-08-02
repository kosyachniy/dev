from func import *
from datetime import datetime

time=datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")

with db:
	db.execute("INSERT INTO note (name, cont, time) VALUES ('Заголовок', 'Содержание', (?))", (time,))