from multiprocessing import Process, Queue

def foo(q):
	q.put('hello')

if __name__ == '__main__':
	q = Queue()

	for i in range(10):
		p = Process(target=foo, args=(q,))
		p.start()

	while True:
		print(q.get())