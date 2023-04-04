import asyncio

from libdev.cfg import cfg
import discord


class DiscordClient(discord.Client): # ClientUser
    def __init__(self, *args, **kwargs):
        discord.Client.__init__(self, **kwargs)

    async def on_ready(self):
        print('Success!')


# @client.event
# async def on_ready():
#     print(f"We have logged in as {client.user}")

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
#     if message.content.startswith("$hello"):
#         await message.channel.send("Hello!")

async def main():
    # intents = discord.Intents.default()
    # intents.message_content = True
    # client = DiscordClient(intents=intents)
    # # await client.login(cfg('discord.token')) # cfg('discord.user'), cfg('discord.pass'))
    # client.run(cfg('discord.token'))

    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    await client.login(cfg('discord.token'))
    client.run()


if __name__ == '__main__':
    asyncio.run(main())

    # intents = discord.Intents.default()
    # intents.message_content = True
    # client = DiscordClient(intents=intents)
    # # await client.login(cfg('discord.token')) # cfg('discord.user'), cfg('discord.pass'))
    # client.run(cfg('discord.token'))

    # intents = discord.Intents.default()
    # intents.message_content = True
    # dc = DiscordClient(intents=intents)
    # email = input('email : ')
    # password = input('password : ')
    # dc.run(email, password)

    # intents = discord.Intents.default()
    # intents.message_content = True
    # client = discord.ClientUser(state={}, data={
    #     # "username": "",
    #     # "id": "0",
    #     # "discriminator": "#123",
    #     # "avatar": "N/A",
    #     'avatar': "5b4b6129f485b13e6aa49411ff4391ee",
    #     'discriminator': "3841",
    #     'id': "439110225975443468",
    #     'pushSyncToken': None,
    #     'tokenStatus': 0,
    #     'username': "Alex Poloz",
    # }) # intents=intents)
    # client.run('g79P0pvkTfTFvxCPEa5z1lpEafT2fP')

    # client = discord.ClientUser



# import discord
# import asyncio
# import datetime


# class DiscordClient(discord.Client):
#     def __init__(self, *args, **kwargs):
#         discord.Client.__init__(self, **kwargs)

#     @asyncio.coroutine
#     def on_ready(self):
#         servers = list(self.servers)
#         for server in servers:
#             if server.name == 'My server':
#                 break

#         for channel in server.channels:
#             if channel.name == 'general':
#                 break

#         now = datetime.datetime.now()
#         yield from self.send_message(channel, 'Api Success! at ' + str(now))
#         print('Success!')
#         yield from self.close()


# if __name__ == '__main__':
#     intents = discord.Intents.default()
#     intents.message_content = True
#     dc = DiscordClient(intents=intents)
#     email = input('email : ')
#     password = input('password : ')
#     dc.run(email, password)
