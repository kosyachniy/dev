import asyncio
from aiogram import Bot, Dispatcher


bot = Bot(token="")
dp = Dispatcher()


@dp.message()
async def handler(msg):
    await msg.answer(f"your id: {msg.chat.id}")


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
