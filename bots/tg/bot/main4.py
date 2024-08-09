import asyncio
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import Command
from dotenv import load_dotenv
from loguru import logger as log


load_dotenv()

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()
router = Router()
dp.include_router(router)


@router.message(Command("start"))
async def start_handler(msg: Message):
    log.info(f"command «start» from {msg.chat.id}")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Button", callback_data="button"),
            ]
        ]
    )
    await msg.reply("Test button", reply_markup=keyboard)


@router.message()
async def message_handler(msg: Message):
    log.info(f"message «{msg.text}» from {msg.chat.id}")
    await msg.answer(f"your id: {msg.chat.id}")


@router.callback_query(F.data == "button")
async def callback_handler(callback: CallbackQuery):
    log.info(f"callback «button» from {callback.message.chat.id}")
    await callback.message.answer("Hello button")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
