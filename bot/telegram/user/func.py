from telethon import TelegramClient

api_id = 12345
api_hash = '0123456789abcdef0123456789abcdef'
phone = '+34600000000'

client = TelegramClient('session_name', api_id, api_hash)
client.connect()

client.sign_in(phone=phone)
me = client.sign_in(code=input())