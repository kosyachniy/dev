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

    with open('migrations/up.sql', 'r') as file:
        data = file.read()
    await conn.fetch(data)

    await conn.fetch('''
        INSERT INTO users (login, name, surname)
            VALUES ('kosyachniy', 'Alexey', 'Poloz')
    ''')

    users = await conn.fetch('SELECT * FROM "users"')
    print(users)

    with open('migrations/down.sql', 'r') as file:
        data = file.read()
    await conn.fetch(data)


asyncio.run(main())
