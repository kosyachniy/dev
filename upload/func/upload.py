import json

import cloudinary
import cloudinary.uploader as upl


with open('keys.json', 'r') as file:
	keys = json.loads(file.read())['cloudinary']

	name = keys['name']
	key = keys['key']
	secret = keys['secret']


def upload(url, result):
	cloudinary.config( 
		cloud_name=name,
		api_key=key,
		api_secret=secret,
	)

	res = upl.upload(url, public_id=result)
	
	return res['url']