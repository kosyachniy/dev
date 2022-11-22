import asyncio
import asyncpg
from libdev.cfg import cfg

async def main():
    conn = await asyncpg.connect(
        host=cfg('db.host'),
        port=cfg('db.port'),
        user=cfg('db.user'),
        password=cfg('db.pass'),
        database=cfg('db.name'),
    )
    print(await conn.fetch('SELECT COUNT(*) FROM products'))

asyncio.run(main())
