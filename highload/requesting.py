from multiprocessing import Process, Manager
import random
import time
import os
# import asyncio


COUNT = 400
COMMANDS = ['''
curl 'https://styletyx.com/api/' \
-X 'POST' \
-H 'Accept: */*' \
-H 'Origin: https://styletyx.com' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer null' \
-H 'Referer: https://styletyx.com/shopping/men' \
-H 'Content-Length: 96' \
-H 'Host: styletyx.com' \
-H 'Accept-Language: en-US,en;q=0.9' \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15' \
-H 'Accept-Encoding: gzip, deflate, br' \
-H 'Connection: keep-alive' \
--data-binary '{"method":"products.filters","params":{"sex":"male","sort":"asc"},"locale":"en","network":"web"}'
''', '''
curl 'https://styletyx.com/api/' \
-X 'POST' \
-H 'Accept: */*' \
-H 'Origin: https://styletyx.com' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer null' \
-H 'Referer: https://styletyx.com/shopping/men' \
-H 'Content-Length: 114' \
-H 'Host: styletyx.com' \
-H 'Accept-Language: en-US,en;q=0.9' \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15' \
-H 'Accept-Encoding: gzip, deflate, br' \
-H 'Connection: keep-alive' \
--data-binary '{"method":"products.get","params":{"count":52,"offset":0,"sex":"male","sort":"asc"},"locale":"en","network":"web"}'
''']


def process(i, data): # async
    print(f"start {i}")
    data[i] = os.system(COMMANDS[random.randint(0,1)])
    print(f"stop {i}")
    # return answer

def main(): # async
    with Manager() as manager:
        start_time = time.time()
        data = manager.dict()

        for i in range(COUNT):
            Process(target=process, args=(i+1, data)).start()
        # answers = await asyncio.gather(
        #     *(process(i+1) for i in range(COUNT))
        # )

        while len(data) != COUNT:
            pass

        print("-" * 100)
        print(('SUCCESS', 'ERROR')[bool(sum(data.values()))], end="")
        # print(('SUCCESS', 'ERROR')[bool(sum(answers))], end="")
        print(f" in {(time.time() - start_time):.3f}s")

# asyncio.run(main())
if __name__ == '__main__':
    main()

# background_tasks = set()

# for i in range(10):
#     task = asyncio.create_task(some_coro(param=i))

#     # Add task to the set. This creates a strong reference.
#     background_tasks.add(task)

#     # To prevent keeping references to finished tasks forever,
#     # make each task remove its own reference from the set after
#     # completion:
#     task.add_done_callback(background_tasks.discard)


# import asyncio
# import subprocess

# async def factorial(name, i):
#     print(f"start {i}")
#     await asyncio.sleep(1)
#     subprocess.run(["ls", "-l"])
#     # answer = os.system(COMMAND)
#     print(f"stop {i}")
#     return 0 # answer

# async def main():
#     # Schedule three calls *concurrently*:
#     L = await asyncio.gather(
#         factorial("A", 2),
#         factorial("B", 3),
#         factorial("C", 4),
#     )
#     print(L)

# asyncio.run(main())


# from multiprocessing import Pool

# def run_command(i):
#     print(f"start {i}")
#     answer = os.system(COMMAND)
#     # subprocess.run(["ls", "-l"])
#     # command = "spark-submit driver.py -i {}".format(path)
#     # subprocess.Popen(command, shell=True)
#     print(f"stop {i}")
#     return answer

# pool = Pool()
# pool.map(run_command, range(1, 6))


# from multiprocessing import Pool, Process

# def f(i):
#     print(f"start {i}")
#     time.sleep(1)
#     answer = os.system(COMMAND)
#     print(f"stop {i}")
#     return answer

# if __name__ == '__main__':
#     for num in range(10):
#         Process(target=f, args=(num,)).start()
#     # with Pool(5) as p:
#     #     print(p.map(f, [1, 2, 3]))
