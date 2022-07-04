"""Simple FIFO queue with Redis to run tasks asynchronously.
===========
Description
===========
This script implements a rudimentary FIFO task queue using Redis's list data
structure. I took a peek under Celery and RQ's source code to understand how
they've implemented the async task queue — harnessing the features of Redis and
Python's multiprocessing paradigm.
Here, I've attempted to emulate a similar task queue — albeit in a much simpler
fashion — to strengthen my grasp on the concept of async task queue. This script
roughly implements the following steps:
-> Task callables are turned into task objects.
-> Each task object has a uuid attached to that.
-> These task objects are then pickle serialized and sent to the broker. Here the
   broker is a Redis database that stores the serialized tasks.
-> Broker stores the tasks in a FIFO queue.
-> A worker runs 4 OS processes that listen to the broker database to find tasks.
-> When a task is found by the worker, it pops that from the FIFO queue, performs
   deserialization, and executes it.
-> The worker sends the task result to a result backend which is just another
   Redis database.
============
Instructions
============
To run the script —
-> Install docker.
-> Spin a Redis instance with the following commands:
```
docker stop dev-redis
docker rm dev-redis
docker run --name dev-redis -d -h localhost -p 6379:6379 redis:alpine
```
-> Install the dependencies:
```
pip install redis
```
-> Run the script:
```
python redis_queue.py
```
-> To inspect the results, connect to Redis DB with RedisInsight, and the results
can be found in Database 1.
=======
License
=======
MIT License.
Copyright (c) 2020 Redowan Delowar.
"""


import logging
import multiprocessing
import pickle
import random
import uuid
from typing import Any, Callable

from redis import Redis

logging.basicConfig(level=logging.INFO)


class SimpleTask:
    """Assign a unique `task_id` to the target function."""

    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        self.id = str(uuid.uuid4())
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def process_task(self):
        """Execute the function."""

        return self.func(*self.args, **self.kwargs)


class RedisQueue:
    """Simplified FIFO queue with Redis."""

    def __init__(self, broker: Redis, result_backend: Redis, queue_name: str):
        self.broker = broker
        self.result_backend = result_backend
        self.queue_name = queue_name

    def enqueue(self, func: Callable, *args: Any, **kwargs: Any):
        # Apply `SimpleTask` on the target function to convert it to a `task` object.
        task = SimpleTask(func, *args, **kwargs)

        # Pickle serialize the `task` object.
        serialized_task = pickle.dumps(task, protocol=pickle.HIGHEST_PROTOCOL)

        # Append the `task` to the right side of Redis's native `list` structure.
        self.broker.rpush(self.queue_name, serialized_task)

        # Return the `task_id` just like Celery.
        return task.id

    def dequeue(self):
        # Fetch the pickle serialized `task` object from Redis.
        serialized_task = self.broker.blpop(self.queue_name)

        # Deserialize the pickled object to the `task` object.
        task = pickle.loads(serialized_task)
        logging.info(f"Task ID: {task.id}, Args: {task.args}, Kwargs: {task.kwargs}")

        # Execute the task here.
        result = task.process_task()

        # Save the result using Redis's `key:val` structure.
        self.result_backend.set(f"{task.id}", result)
        logging.info("Task processing complete.")

    def get_length(self):
        return self.broker.llen(self.queue_name)


def worker(queue: RedisQueue, max_worker: int = 4):
    """Mimicks the celery worker."""

    def _execute_task(queue):
        if queue.get_length() > 0:
            queue.dequeue()
        else:
            logging.info("No tasks in the queue")

    processes = []

    logging.info(f"Running tasks with {max_worker} processes!")
    while queue.get_length() != 0:
        for _ in range(max_worker):
            p = multiprocessing.Process(target=_execute_task, args=(queue,))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()


if __name__ == "__main__":
    # Instantiate Redis `broker` and `result_backend` connections.
    broker = Redis("localhost", db=0)
    result_backend = Redis("localhost", db=1)

    # Instantiate the `RedisQueue` object with the queue name `default`.
    rq = RedisQueue(broker, result_backend, "default")

    # Define a task to be run asynchronously.
    def task(start: int, end: int):
        return random.randint(start, end)

    # Assigning 10 tasks to be carried out by the worker, usually you'd do
    # this in a separate module.
    for start, end in zip(range(10), range(100, 1000, 100)):
        rq.enqueue(task, start, end)

    # Spawn 4 parallel processes, fetch tasks from the queue and execute them
    # asynchronously.
    worker(rq)
