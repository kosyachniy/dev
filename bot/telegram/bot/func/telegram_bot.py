from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater

import json
import time


with open('keys.json', 'r') as file:
	TOKEN = json.loads(file.read())['tg_token']

updater = Updater(TOKEN)


def keyboard(table):
	table = [[InlineKeyboardButton(col[0], callback_data=col[1]) for col in row] for row in table]
	return InlineKeyboardMarkup(table)