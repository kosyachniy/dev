from instagram.client import InstagramAPI

client_id='d773986be65d404582e3b2933a6614b7'
client_secret='34bfa7f17a6b426a8e3d97b69530706e'
access_token='5532209280.d773986.a31798ba944545eb8e742360d36f9535'

api=InstagramAPI(access_token=access_token,client_secret=client_secret)
recent_media,next_=api.user_recent_media(user_id='yourrrgram',count=10)
for media in recent_media:
	print(media.caption.text)