import sys, threading
from user import search
from trends import trends
from follow import follow
from twit import post

#Фолловинг 			1000/день
#Твитить			2400/день
#Сообщение			1/минута
#Список				1/минута

#python3 main.py ME NEW POST RUSSIAN USER

#Search
#	user
#	trends
#Action
#	follow
#	twit
#Followers
#	new
#	old

with open('set.txt', 'r') as file:
	s=loads(file.read())

arg=len(sys.argv)
s['default']['StartFollow']=sys.argv[5] if arg>=6 else 'PomidorWatsona'
s['default']['NotRussian']=False if arg>=5 and sys.argv[4]=='ru' else True
s['default']['Post']=False if arg>=4 and sys.argv[3]=='x' else True
me=sys.argv[1] if arg>=2 else ''

with open('set.txt', 'w') as file:
	print(dumps(s, indent=4), file=file)

#Поиск пользователей: подписка, твиты
threading.Thread(target=search, args=(me,)).start()
#Анализ трендов: теги, твиты, пользователи
threading.Thread(target=trends, args=(me,)).start()
#Автоподписка
threading.Thread(target=follow, args=(me,)).start()
#Автопостинг
if p: threading.Thread(target=post, args=(me,)).start()
#Подписка на новых и сообщения
#Отписка от старых невзаимных и некативных
#Эмулятор живого: общение, ретвиты, лайки, списки