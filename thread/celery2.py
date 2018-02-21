from celery import Celery

app = Celery('celery2', broker='pyamqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y