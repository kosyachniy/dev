import sys, threading
from autopost import post
from autofollow import user
from followers import userr
#from unfollow import unf

#Фолловинг 			1000/день
#Твитить			2400/день
#Сообщение			1/минута
#Список				1/минута

#python3 main.py kosyachniy x x PomidorWatsona ...

arg=len(sys.argv)
if arg==6:
	last=sys.argv[5]
else:
	last=''
if arg>=5:
	start=sys.argv[4]
else:
	start=''
if arg>=4 and sys.argv[3]=='x':
		p=False
else:
	p=True
if arg>=3 and sys.argv[2]=='x':
		m=False
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
threading.Thread(target=user,args=(me,start)).start()
#Контроль новых подписчиков: сообщения, подписка (при каждой подписке)
threading.Thread(target=userr,args=(me,last,m)).start()
#Удалять тех, кто в течении недели не подписался (1/день)
#threading.Thread(target=unf,args=(me,)).start()