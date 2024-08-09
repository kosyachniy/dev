import asyncio
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from loguru import logger


load_dotenv()
token = os.getenv("TOKEN")
dp = Dispatcher()
router = Router()


async def main():
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


@router.message(Command("start"))
async def start_handler(msg: Message):
    logger.info("Новое стартовое сообщение")
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Press the button", callback_data="button"),
            ]
        ]
    )
    await msg.reply(text="Test button", reply_markup=inline_keyboard)


@router.message()
async def message_handler(msg: Message):
    logger.info(f"Входящее сообщение: {msg.text} от @{msg.from_user.username}")
    await msg.answer(f"Твой ID: {msg.from_user.id}")


@router.callback_query(F.data == "button")
async def callback_handler(callback: CallbackQuery):
    await callback.message.answer(f"Hello button")


if __name__ == "__main__":
    asyncio.run(main())
