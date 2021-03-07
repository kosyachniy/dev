from func.tg_bot import bot


CHAT = -1001390390608
USERS = (373406030, 136563129, 1229366790)


def check_entry(chat, user):
	try:
		user_type = bot.get_chat_member(chat, user).status
		# print(user_type)
		if user_type in ('creator', 'administrator', 'member'):
			return True
		return False
	except:
		return False


for user in USERS:
	print(user, end=' ')
	print('YNEOS'[not check_entry(CHAT, user)::2])