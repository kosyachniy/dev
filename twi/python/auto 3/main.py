import sys, threading
from autopost import post
from autofollow import search
from followers import new
from unfollow import unf

#Фолловинг 			1000/день
#Твитить			2400/день
#Сообщение			1/минута
#Список				1/минута

arg=len(sys.argv)
u=False if arg==7 and sys.argv[6]=='x' else True
start=sys.argv[5] if arg>=6 else ''
l=False if arg>=5 and sys.argv[4]=='ru' else True
p=False if arg>=4 and sys.argv[3]=='x' else True
last=''
m=True
if arg>=3:
	if sys.argv[2]=='x':
		m=False
	elif sys.argv[2]!='v':
		last=sys.argv[2]
me=sys.argv[1] if arg>=2 else ''


Search
	user
	trends
Followers
	new
	old
Action
	follow
	twit



#Автопостинг твитов на базе интернета / популярных твитов
if p: threading.Thread(target=post, args=(me,)).start()
#Подписываться для накрутки + проверка языка
threading.Thread(target=search, args=(me, l, start)).start()
#Контроль новых подписчиков: сообщения, подписка (при каждой подписке)
th=threading.Thread(target=new, args=(me, m, last))
th.daemon=True
th.start()
#Удалять тех, кто в течении недели не подписался (1/день)
if u: threading.Thread(target=unf, args=(me,)).start()