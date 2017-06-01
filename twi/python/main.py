import sys, threading
from autopost import post
from autofollow import user
from followers import userr

arg=len(sys.argv)
if arg==4:
	last=sys.argv[3]
else:
	last=''
if arg>=3:
	start=sys.argv[2]
else:
	start=''
if arg>=2:
	me=sys.argv[1]
else:
	me='deepinmylife'

#Автопостинг твитов на базе интернета / популярных твитов (твитить 2400 в день)
threading.Thread(target=post,args=(me)).start()
#Подписываться для накрутки, проверка языка (фолловинг 1 раз в минуту, список 1 раз в минуту)
threading.Thread(target=user,args=(me,start)).start()
#Подписываться на недавно подписавшихся меня ради фолловинга (при каждой подписке)
threading.Thread(target=userr,args=(me,last)).start()