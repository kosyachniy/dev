import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

client_id = ''
client_secret = ''

# Создайте OAuth2-сессию с использованием идентификатора приложения и секретного ключа
client = BackendApplicationClient(client_id=client_id)
print('!', dir(client), client.access_token, client.refresh_token, client.code, client.client_id, client.state)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(
    token_url='https://discord.com/api/oauth2/token',
    client_id=client.client_id,
    # client_secret=client_secret,
)

print(token)
