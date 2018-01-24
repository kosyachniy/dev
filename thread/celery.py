#from celery import Celery

from celery.decorators import task
from celery.decorators import periodic_task
from celery.task.schedules import crontab

#app = Celery('hello', broker='amqp://guest@localhost//')

@task
def hello():
	print('123')


def foo():
	print('Start!')
	hello()


from multiprocessing import Process

for i in range(10):
	p = Process(target=foo, args=(q,))
	p.start()