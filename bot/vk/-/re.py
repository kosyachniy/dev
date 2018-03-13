from func.vk_user import *
from time import sleep

while True:
	for i in read():
		send(i[0], ' | '.join([str(i) for i in info(i[1])]))

	sleep(1)