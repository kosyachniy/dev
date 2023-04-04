import discord
from discord.ext import commands

client_id = ''
client_secret = ''
redirect_uri = 'https://chill.services/discord'
scope = 'identify'

# auth_url = f'https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}'
# print(auth_url)



# rLi7GKL2EA9Qp5NNIi90pDvRzim1qK


import requests

code = ''

# token_url = 'https://discord.com/api/oauth2/token'
# payload = {
#     'client_id': client_id,
#     'client_secret': client_secret,
#     'grant_type': 'authorization_code',
#     'code': code,
#     'redirect_uri': redirect_uri,
#     'scope': scope
# }
# headers = {
#     'Content-Type': 'application/x-www-form-urlencoded'
# }
# response = requests.post(token_url, data=payload, headers=headers)
# print(response.json())


# {'access_token': '', 'expires_in': 604800, 'refresh_token': '', 'scope': 'email connections identify guilds', 'token_type': 'Bearer'}


import discord
from discord.ext import commands

token = ''

bot = commands.Bot(command_prefix='!', self_bot=True)
bot.run(token)

@bot.event
async def on_ready():
    user = await bot.fetch_user(bot.user.id)
    print(user.name)
