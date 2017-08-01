import sqlite3

auth=sqlite3.connect('1.db')
db=auth.cursor()

db.execute('''CREATE TABLE stocks (id int, name text, cont text, time text)''')

db.execute("INSERT INTO stocks VALUES (1, 'Заголовок', 'Содержание', '01.08.2017 03:01:00')")

auth.commit()
auth.close()