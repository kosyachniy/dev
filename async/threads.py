import asyncio
import concurrent.futures


async def task1():
    while True:
        print("Task 1 is running...")
        await asyncio.sleep(1)

async def task2():
    while True:
        print("Task 2 is running...")
        await asyncio.sleep(2)

async def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        await asyncio.gather(
            await loop.run_in_executor(executor, task1),
            await loop.run_in_executor(executor, task2)
        )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
