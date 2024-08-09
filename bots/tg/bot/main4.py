import asyncio
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv
from loguru import logger as log


load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()
router = Router()
dp.include_router(router)


@router.message(Command("start"))
async def start_handler(msg):
    log.info(f"command «start» from {msg.chat.id}")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Button", callback_data="button"),
            ],
        ],
    )
    await msg.reply("start menu", reply_markup=keyboard)


@router.message()
async def message_handler(msg):
    log.info(f"message «{msg.text}» from {msg.chat.id}")
    await msg.answer(f"your id: {msg.chat.id}")


@router.callback_query(lambda callback: callback.data == "button")
async def callback_handler(callback):
    log.info(f"callback «{callback.data}» from {callback.message.chat.id}")
    await callback.message.answer("button menu")


async def main():
    log.info(f"start bot @{(await bot.get_me()).username}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
