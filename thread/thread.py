import threading

def writer(x, event_for_wait, event_for_set):
    for i in range(10):
        event_for_wait.wait() # wait for event
        event_for_wait.clear() # clean event for future
        print(x)
        event_for_set.set() # set event for neighbor thread

# init events
e1 = threading.Event()
e2 = threading.Event()

# init threads
t1 = threading.Thread(target=writer, args=(0, e1, e2))
t2 = threading.Thread(target=writer, args=(1, e2, e1))

# start threads
t1.start()
t2.start()

e1.set() # initiate the first event

# join threads to the main thread
t1.join()
t2.join()