from encodings.aliases import aliases


text_encrypted = '                                Ð¼ÐµÐ¼Ñ Ð¿ÑÐ¾ Ð´ÐµÐ²ÑÑÐµÐº                            '
fragment_decrypted = 'мем'


cods = set(aliases.values())
text_encrypted = text_encrypted.strip()

for code_enc in cods:
	try:
		text = text_encrypted.encode(code_enc)
		# print(text)

		for code_dec in cods:
			try:
				text_decrypted = text.decode(code_dec)
				# print(text_decrypted)

				if fragment_decrypted in text_decrypted:
					print(text_decrypted)
					print(code_enc, '->', code_dec)

			except:
				pass
	except:
		pass