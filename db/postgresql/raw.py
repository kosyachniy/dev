import asyncio
import asyncpg


async def main():
    # conn = await asyncpg.connect('postgresql://postgres:password@localhost/main')
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='password',
        database='main',
    )

    await conn.fetch('''
        CREATE TABLE "users" (
            "id" SERIAL NOT NULL PRIMARY KEY,
            "status" SMALLINT NOT NULL DEFAULT 3,
            "image" TEXT,
            "login" TEXT COLLATE "en_US" CHECK("login" ~ '\S+') UNIQUE,
            "name" TEXT COLLATE "en_US" CHECK("name" ~ '\S+'),
            "surname" TEXT COLLATE "en_US" CHECK("surname" ~ '\S+'),
            "mail" TEXT COLLATE "en_US" CHECK("mail" ~ '\S+') UNIQUE,
            "password" TEXT,
            "phone" INTEGER UNIQUE,
            "lang" TEXT NOT NULL DEFAULT 'ru' CHECK("lang" ~ '\S+'),
            "created" TIMESTAMP NOT NULL DEFAULT NOW(),
            "updated" TIMESTAMP NOT NULL DEFAULT NOW(),
            "extra" JSONB NOT NULL DEFAULT '{}'::JSONB
        )
    ''')
    # CONSTRAINT users_pkey PRIMARY KEY ("id")

    await conn.fetch('''
        INSERT INTO users (login, name, surname)
            VALUES ('kosyachniy', 'Alexey', 'Poloz')
    ''')

    users = await conn.fetch('SELECT * FROM "users"')
    print(users)

    await conn.fetch('DROP TABLE "users"')


asyncio.get_event_loop().run_until_complete(main())
# asyncio.run(main())
