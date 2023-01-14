import re


def only_words(cont):
	return re.split(r'[^a-zA-Zа-яА-Я-]', cont)