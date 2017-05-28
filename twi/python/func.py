import tweepy

def auth(user='deepinmylife'):
	if user=='deepinmylife':
		consumer_key='dyLgjQsoCQHxaLSk1baLOCEQe'
		consumer_secret='tEnKUNJhNlj7JYTZ5pesIyFYhqQckqbEn84O7QcfTaYTb5bGTp'
		access_key='3110781773-wiWQkS9564FBEjEb4pzwrPAJdIvtmQFuu4ofblj'
		access_secret='H9u8EQG10XwQIP1vufpVqMZ4NgIpfWPcH0f6FuDq1UKA6'
	elif user=='kosyachniy':
		consumer_key='jARMeUTgjWhDSWOSbs0pfQYz4'
		consumer_secret='stRnOnA3KRpaCI3hjyJyo0eLedQNflQ4FuvudvXj37mSLX7tPa'
		access_key='4100776272-4VpvJNSkyhG9kWXfhRHyI3eTEeBRYRABiIqzusU'
		access_secret='RHcdHHf0TyHBxtfxHyRCgmB41r7c6gnVgUHH7SEf1Uqi9'

	aut=tweepy.OAuthHandler(consumer_key,consumer_secret)
	aut.set_access_token(access_key,access_secret)
	api=tweepy.API(aut)
	return api