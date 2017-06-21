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
		
		#consumer_key='mcactbAgFofues75dpMkFKLsg'
		#consumer_secret='2H1KU0cR3kcYXgHgfFLnLwzqYdF7Ie5QBsqIVYA7zzN6jEN7QU'
		#access_key='3110781773-ak4xx5HgoxzxXEyjAZEKRWdmP5lShFoAhPpjymV'
		#access_secret='1Y5G4s10BHdGjrA3Lxh7TNblLbJXfkSCd1EUaQL35NP0W'

	aut=tweepy.OAuthHandler(consumer_key,consumer_secret)
	aut.set_access_token(access_key,access_secret)
	api=tweepy.API(aut)
	return api