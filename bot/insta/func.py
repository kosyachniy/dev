import json

from instagram.client import InstagramAPI


with open('keys.json', 'r') as file:
	keys = json.loads(file.read())['instagram']

	access_token = keys['token']
	client_secret = keys['secret']


api=InstagramAPI(access_token=access_token, client_secret=client_secret)
recent_media,next_=api.user_recent_media(user_id='yourrrgram', count=10)

for media in recent_media:
	print(media.caption.text)