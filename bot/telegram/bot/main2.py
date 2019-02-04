from func.tg_bot import updater, keyboard
from telegram.ext import Filters, MessageHandler, CallbackQueryHandler


# @process
def echo(bot, update):
	print(update)
	print('-'*100)

	user = update.message.from_user.id

	if user != 136563129:
		update.message.reply_text('Нет доступа!')
		return

	message = update.message.text

	update.message.reply_text(message, reply_markup=keyboard([[('Да', 'y'), ('Нет', 'n')], [('Позже', 'later'),]]))


def button(bot, update):
	query = update.callback_query

	bot.edit_message_text(text="Selected option: {}".format(query.data), chat_id=query.message.chat_id, message_id=query.message.message_id)


if __name__ == '__main__':
	# updater.dispatcher.add_handler(CommandHandler('start', start))
	updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
	updater.dispatcher.add_handler(CallbackQueryHandler(button))
	# updater.dispatcher.add_error_handler(error)

	updater.start_polling()
	updater.idle()