import sys, tweepy, time

def auth(user='deepinmylife'):	
	if user=='deepinmylife':
		consumer_key='dyLgjQsoCQHxaLSk1baLOCEQe'
		consumer_secret='tEnKUNJhNlj7JYTZ5pesIyFYhqQckqbEn84O7QcfTaYTb5bGTp'
		access_key='3110781773-wiWQkS9564FBEjEb4pzwrPAJdIvtmQFuu4ofblj'
		access_secret='H9u8EQG10XwQIP1vufpVqMZ4NgIpfWPcH0f6FuDq1UKA6'
	elif user=='kosyachniy':
		consumer_key='vgCY4P69DWWqGYeyigkoB6u7G'
		consumer_secret='I9LvATKcjdM1ZVIqNkfnp3pN0Xq4qFyOK4NvF1px63eucJfpxG'
		access_key='4100776272-oHAXuvEl9YZeTWHMF2PboLUKn2oZ9KXjcqgkoxH'
		access_secret='Hbihu1nHxXyn8kY7OrJGBwC3888XM0UP1H8tn8Lfauu3e'

	aut=tweepy.OAuthHandler(consumer_key,consumer_secret)
	aut.set_access_token(access_key,access_secret)
	api=tweepy.API(aut)
	return api