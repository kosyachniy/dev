from json import *

a=dumps({'message':['Привет! Давай знакомиться. Я взаимный)) Подписывайся - https://www.instagram.com/mr.poloz/','https://www.instagram.com/mr.poloz/'], 'default':{'user':'deepinmylife', 'bMessage':True, 'last':'', 'bPost':True, 'bAllCountry':True, 'start':'PomidorWatsona', 'bAutoUnfollow':True}}, indent=4)
with open('set.txt', 'w') as file:
	print(a, file=file, end='')