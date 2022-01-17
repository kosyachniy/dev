from encodings.aliases import aliases
import urllib.parse


text_encrypted = '                                Ð¼ÐµÐ¼Ñ Ð¿ÑÐ¾ Ð´ÐµÐ²ÑÑÐµÐº                            '
fragment_decrypted = 'мем'
# text_encrypted = '\ud83d\udc4d'
# fragment_decrypted = '👍'
# text_decrypted = '\u003cfoo\u003e'
# fragment_encrypted = '<foo>'


cods = set(aliases.values())
text_encrypted = text_encrypted.strip()


print('encode → decode')
print('-'*25)
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
                    print(code_enc, '→', code_dec)

            except:
                pass
    except:
        pass


print()
print('URL parse')
print('-'*25)
print(urllib.parse.unquote(text_encrypted))

print()
print('decode → encode')
print('-'*25)
for code_enc in cods: # {'unicode_escape'}: hex
    try:
        text = text_encrypted.encode(code_enc).decode('unicode_escape')
        print(text)

        # for code_dec in cods:
        #     try:
        #         text_decrypted = text.encode(code_dec)
        #         # print(text_decrypted)

        #         if fragment_decrypted in text_decrypted:
        #             print(text_decrypted)
        #             print(code_enc, '→', code_dec)

        #     except:
        #         pass
    except:
        pass
