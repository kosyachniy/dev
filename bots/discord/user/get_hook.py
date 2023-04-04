import requests


token = {'access_token': '', 'expires_in': 604800, 'refresh_token': '', 'scope': 'connections guilds identify email', 'token_type': 'Bearer', 'webhook': {'type': 1, 'id': '1083767716898418803', 'name': 'chill', 'avatar': 'd9b4075d24ac26f6b563af1a4fdf32e0', 'channel_id': '1083764068562771968', 'guild_id': '667320783579774977', 'application_id': '1083747207385186424', 'token': '', 'url': 'https://discord.com/api/webhooks/1083767716898418803/'}}
headers = {
    'Content-Type': 'application/json'
}
data = {
}

# res = requests.post(f"https://discord.com/api/webhooks/{token['webhook']['id']}/{token['webhook']['token']}", headers=headers, data=data)
# res.raise_for_status()
# print(res.json())
# # print(res.text)


res = requests.get(f"https://discord.com/api/webhooks/{token['webhook']['id']}/{token['webhook']['token']}/messages/1", headers=headers, data=data)
# res.raise_for_status()
# print(res.json())
print(res.text)
