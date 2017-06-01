import sys, threading
from autopost import post
from autofollow import user
from followers import userr

#Получение списка	1/минута
#Фолловинг 			1000/день
#Твитить			2400/день
#Сообщение			1/минута

#python3 main.py kosyachniy x PomidorWatsona ...

arg=len(sys.argv)
if arg==5:
	last=sys.argv[4]
else:
	last=''
if arg>=4:
	start=sys.argv[3]
else:
	start=''
if arg==3:
	if sys.argv[2]=='x':
		t=False
else:
	t=True
if arg>=2:
	me=sys.argv[1]
else:
	me='deepinmylife'

#Автопостинг твитов на базе интернета / популярных твитов
if t:
	threading.Thread(target=post,args=(me)).start()
#Подписываться для накрутки + проверка языка
threading.Thread(target=user,args=(me,start)).start()
#Контроль новых подписчиков: сообщения, подписка (при каждой подписке), удалять тех, кто в течении недели не подписался (1/день)
threading.Thread(target=userr,args=(me,last)).start()