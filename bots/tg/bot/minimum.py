import telebot

token = '0000000000:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
chat_id = 'AnnouncementsPUNK'

text = 'Для активации бота отправьте 100₽ на 5536 9137 9103 8041'

bot = telebot.TeleBot(token)

mes = bot.send_message(f'@{chat_id}', text)
print(mes.message_id)

# bot.delete_message(f'@{chat_id}', 1022)