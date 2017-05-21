from func import *
import time

with open('db.txt','r') as file:
	for i in file:
		name=i[0:-1]
		if name:
			api.get_user(name).follow()
			print(name)
			time.sleep(60)