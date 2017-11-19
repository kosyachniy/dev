from func import *

import time

def mess(cont):
	print(cont.status)
	time.sleep(2)
	#print(dir(cont))
	#print(cont.to_dict())
	'''
	if 'status' not in dir(cont):
		print(cont.stringify().title())
	'''

while True:
	client.add_update_handler(mess)