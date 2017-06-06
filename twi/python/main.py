import sys, threading
from autopost import post
from autofollow import user
from followers import userr
from unfollow import unf

#Фолловинг 			1000/день
#Твитить			2400/день
#Сообщение			1/минута
#Список				1/минута

#python3 main.py kosyachniy x x ru PomidorWatsona x
#python3 main.py deepinmylife v v all zadrotstvo v
#python3 main.py deepinmylife x v ru zadrotstvo x

arg=len(sys.argv)
if arg>=7 and sys.argv[6]=='x':
	u=False
else:
	u=True
if arg>=6:
	start=sys.argv[5]
else:
	start=''
if arg>=5 and sys.argv[4]=='ru':
	l=False
else:
	l=True
if arg>=4 and sys.argv[3]=='x':
	p=False
else:
	p=True
if arg>=3:
	last=''
	if sys.argv[2]=='x':
		m=False
	elif sys.argv[2]=='v':
		m=True
	else:
		last=sys.argv[2]
else:
	m=True
if arg>=2:
	me=sys.argv[1]
else:
	me='deepinmylife'

#Автопостинг твитов на базе интернета / популярных твитов
if p:
	threading.Thread(target=post,args=(me,)).start()
#Подписываться для накрутки + проверка языка
threading.Thread(target=user,args=(me,l,start)).start()
#Контроль новых подписчиков: сообщения, подписка (при каждой подписке)
threading.Thread(target=userr,args=(me,m,last)).start()
#Удалять тех, кто в течении недели не подписался (1/день)
if u:
	threading.Thread(target=unf,args=(me,)).start()