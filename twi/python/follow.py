from func import *
import time

with open('db.txt','r') as file:
	for i in file:
		api.get_user(i[0:-1]).follow()
		time.sleep(60)