import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
from loguru import logger as log


load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(msg):
    log.info(f"command «start» from {msg.chat.id}")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="button", callback_data="button"),
            ],
        ],
    )
    await msg.reply("start menu", reply_markup=keyboard)


@dp.message()
async def message_handler(msg):
    log.info(f"message «{msg.text}» from {msg.chat.id}")
    await msg.answer(f"your id: {msg.chat.id}")


@dp.callback_query(lambda cb: cb.data == "button")
async def callback_handler(cb):
    log.info(f"callback «{cb.data}» from {cb.message.chat.id}")
    await cb.message.answer("button menu")


async def main():
    log.info(f"start bot @{(await bot.get_me()).username}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
