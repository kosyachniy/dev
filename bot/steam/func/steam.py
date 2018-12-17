import json

from steam import WebAPI, SteamClient


with open('keys.json') as file:
	token = json.loads(file.read())['token']

api = WebAPI(key=token)