import sys
from json import *
from multiprocessing import Process, Manager
from user import search
from trends import trends
from follow import follow
from twit import twit
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

x=Manager().dict()
#Считывание файла настроек в глобальные переменны и обновление
with open('set.txt', 'r') as file:
	x=loads(file.read())['default']

arg=len(sys.argv)
#Исправить чтобы не менял, если не заданы
if arg==7: x['Unfollow']=False if sys.argv[6]=='x' else True
#Добавить топ-пользователей?
if arg>=6: x['StartFollow']=sys.argv[5]
if arg>=5: x['NotRussian']=False if sys.argv[4]=='ru' else True
if arg>=4: x['Post']=False if sys.argv[3]=='x' else True
if arg>=3:
	last=''
	m=True
	if sys.argv[2]=='x':
		m=False
	elif sys.argv[2]!='v':
		last=sys.argv[2]
	x['NewFollowers']=m
	x['LastFollowers']=last
if arg>=2: x['Me']=sys.argv[1]

#x['work']=True

#Возобновление процессов при ошибке
#Поиск пользователей: подписка, твиты
p1=Process(target=search, args=(x,))
#Анализ трендов: теги, твиты, пользователи
p2=Process(target=trends, args=(x,))
#Подписываться для накрутки
p3=Process(target=follow, args=(x,))
#Автопостинг твитов на базе интернета / популярных твитов
if x['Post']: p4=Process(target=twit, args=(x,))
#Контроль новых подписчиков: подписка, сообщения
#th=threading.Thread(target=new, args=(me, m, last))
#th.daemon=True
#th.start()
#Отписка от давних / Удалять тех, кто в течении недели не подписался (1/день)
#if u: threading.Thread(target=unf, args=(me,)).start()
#Эмулятор живого: общение, ретвиты, лайки, списки
#

p1.start()
p2.start()
p3.start()
if x['Post']: p4.start()

#q=input()
#if q: x['work']=False

p1.join()
p2.join()
p3.join()
if x['Post']: p4.join()