import sys, tweepy, time

def auth(user='deepinmylife'):	
	if user=='kosyachniy':
		consumer_key='vgCY4P69DWWqGYeyigkoB6u7G'
		consumer_secret='I9LvATKcjdM1ZVIqNkfnp3pN0Xq4qFyOK4NvF1px63eucJfpxG'
		access_key='4100776272-oHAXuvEl9YZeTWHMF2PboLUKn2oZ9KXjcqgkoxH'
		access_secret='Hbihu1nHxXyn8kY7OrJGBwC3888XM0UP1H8tn8Lfauu3e'
	else:
		consumer_key='87RK9id1FnxGAeFRw15dPwQbA'
		consumer_secret='hPK7FOw6FnXIncz5VrId6CckyYns3QYGEZamzumlCQepMsaxQr'
		access_key='3110781773-JRSvfLqnxjW1UoPCe7wcDxzuf2Obbif67pH6GlM'
		access_secret='Ya9Mooiae17zDhyVrxvc0ZfQoE11PAMVP79LqqnQvYCtX'

	aut=tweepy.OAuthHandler(consumer_key,consumer_secret)
	aut.set_access_token(access_key,access_secret)
	api=tweepy.API(aut)
	return api