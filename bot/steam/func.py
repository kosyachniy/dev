import json
from steam import WebAPI, SteamClient

with open('set.txt') as file:
	api=WebAPI(key=json.loads(file.read())['token'])