import sys, threading
from user import search
from trends import trends
from follow import follow
from twit import apost
#from new import new
#from old import old

#Фолловинг 			1000/день
#Твитить			2400/день
#Сообщение			1/минута
#Список				1/минута

#python3 main.py ME NEW POST RUSSIAN USER OLD
#python3 main.py deepinmylife x x ru PomidorWatsona x

#Search
#	user
#	trends
#Action
#	follow
#	twit
#Followers
#	new
#	old

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

#Поиск пользователей: подписка, твиты
threading.Thread(target=search, args=(me, start, l, p)).start()
#Анализ трендов: теги, твиты, пользователи
threading.Thread(target=trends, args=(me,)).start()
#Подписываться для накрутки
threading.Thread(target=follow, args=(me,)).start()
#Автопостинг твитов на базе интернета / популярных твитов
if p: threading.Thread(target=apost, args=(me,)).start()
#Контроль новых подписчиков: подписка, сообщения
#th=threading.Thread(target=new, args=(me, m, last))
#th.daemon=True
#th.start()
#Отписка от давних / Удалять тех, кто в течении недели не подписался (1/день)
#if u: threading.Thread(target=unf, args=(me,)).start()
#Эмулятор живого: общение, ретвиты, лайки, списки
#