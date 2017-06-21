import sys, tweepy, time
from json import *

def auth(user='deepinmylife'):	
	consumer_key='vveAVFha4hTcjUStnOf0hwEwQ'
	consumer_secret='F8tFzORTE8DzAAYnz5hHxCBRAClPWf4ABhuGn03GHZ5w2QJtbP'
	if user=='kosyachniy':
		access_key=''
		access_secret=''
	elif user=='alexpoloz':
		access_key='393195793-5OHIbf9wTGHaTbk3BBpGyDF0KxIo61n7bKgxSom3'
		access_secret='wFjDOGxoHzp1gj7ZyUOqdjNmA5gg8ga74RqdlPA7TzHSj'
	else:
		access_key='3110781773-HNd7zymonJSoJmbzHyQ4IL6O7y8f3XmbIxha4pN'
		access_secret='rrz2R22vtXezxpjMeFC9gGj0tXPMhnRRZOmMdaDKvGlG7'

	aut=tweepy.OAuthHandler(consumer_key,consumer_secret)
	aut.set_access_token(access_key,access_secret)
	api=tweepy.API(aut)
	return api