from multiprocessing import Process, Queue, current_process
 
def worker_write(q):
    for i in range(1000):
        q.put({"key1": 'test', 'key2': 'test', 'key3': 'test'})
    q.put(None)
    print(current_process().name + ' -> End.')
 
if __name__ == '__main__':
    results = Queue()
    pr = []
    num_workers = 2
    for i in range(num_workers):
        process = Process(target=worker_write, args=(results,))
        process.start()
        pr.append(process)
    
    while num_workers:
        item = results.get()
        if item is None:
            num_workers -= 1
    for process in pr:
        process.join()