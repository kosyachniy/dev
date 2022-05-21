import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='password',
        database='main',
    )

    with open('migrations/down.sql', 'r') as file:
        data = file.read()
    try:
        await conn.fetch(data)
    except Exception as e:
        print(e)

    with open('migrations/up.sql', 'r') as file:
        data = file.read()
    await conn.fetch(data)


asyncio.run(main())
