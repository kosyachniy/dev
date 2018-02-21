# -*- coding: utf-8 -*-
from queue import Queue
from threading import Thread

# количество потоков обслуживающих очередь
num_worker_threads=2

def do_work(item):
    """
    Функция иммитирующая полезную работу
    """

    s=str(item)
    print(s[::-1])

def worker():
    """
    Основной код здесь
    """

    while True:
        # Получаем задание из очереди
        item = q.get()
        do_work(item)
        # Сообщаем о выполненном задании
        q.task_done()

def source():
    """
    Функция генерирующая данные для очереди
    """

    for i in range(100, 105):
        yield i
    
# Создаем FIFO очередь
q = Queue()
# Создаем и запускаем потоки, которые будут обслуживать очередь
for i in range(num_worker_threads):
    t = Thread(target=worker)
    t.setDaemon(True)
    t.start()

# Заполняем очередь заданиями 
for item in source():
    q.put(item)

# Ставим блокировку до тех пор пока не будут выполнены все задания
q.join()