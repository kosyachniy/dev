import asyncio

# from tgio import Telegram
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor


API_TOKEN = ""
CHANNEL_ID = -1001142824902


# tg = Telegram(API_TOKEN)
bot = Bot(token=API_TOKEN)


async def main():
    # await tg.send(CHANNEL_ID, 'test', files=[
    #     're.png',
    # ], buttons=[{
    #     'name': 'Открыть',
    #     'data': f'https://yandex.ru/',
    # }])
    try:
        # Создание группы медиа для фото
        media = types.MediaGroup()
        # Здесь добавляем фото. Вместо 'file_id_1', 'file_id_2' используй реальные file_id фото
        media.attach_photo("file_id_1", "Описание первого фото")
        media.attach_photo("file_id_2", "Описание второго фото")

        # Отправка группы фото в канал
        await bot.send_media_group(CHANNEL_ID, media=media)

        # Создание кнопки
        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(
            text="Нажми меня", callback_data="button_click"
        )
        keyboard.add(button)

        # Отправка сообщения с кнопкой в канал
        await bot.send_message(CHANNEL_ID, "Выбери действие:", reply_markup=keyboard)
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())


@dp.callback_query_handler(lambda c: c.data == "button_click")
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Кнопка нажата!")


if __name__ == "__main__":
    executor.start_polling(dp)
