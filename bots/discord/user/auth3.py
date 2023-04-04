import discord
from discord.ext import commands
import requests

client_id = ''
client_secret = ''
redirect_uri = 'https://chill.services/discord'
scope = 'identify'

auth_url = f'https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}'
print(auth_url)

code = input('Введите код доступа: ')

token_url = 'https://discord.com/api/oauth2/token'
payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': redirect_uri,
    'scope': scope
}
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}
response = requests.post(token_url, data=payload, headers=headers)
response_data = response.json()

access_token = response_data['access_token']

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
# client = discord.Client()
client.run(access_token, bot=False)

@client.event
async def on_ready():
    user = await client.fetch_user(client.user.id)
    print(user.name)
