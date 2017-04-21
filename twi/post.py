import tweepy, codecs, sys
if sys.version_info[0]>=3:
	from urllib.request import urlretrieve, urlopen
else:
	from urllib import urlretrieve, urlopen

consumer_key='8Y2o5PjasQkVmvoxVQBLyVs4F'
consumer_secret='2r4KPBm8kCcKsNrwkzSQRH4IkDqbxhVrgVcAmvfoyfXbZUNm1L'
access_key='3110781773-4I27iEchYIxqZmIQOgt18b2ehZUHkdEpWKRPuRO'
access_secret='OZj9w6TRUQoeVCgk3pShYOTFWasvSx3ebgOXn6lJQyngy'

#consumer_key='jARMeUTgjWhDSWOSbs0pfQYz4'
#consumer_secret='stRnOnA3KRpaCI3hjyJyo0eLedQNflQ4FuvudvXj37mSLX7tPa'
#access_key='4100776272-4VpvJNSkyhG9kWXfhRHyI3eTEeBRYRABiIqzusU'
#access_secret='RHcdHHf0TyHBxtfxHyRCgmB41r7c6gnVgUHH7SEf1Uqi9'

url='http://t30p.ru/'
adr='http://api.forismatic.com/api/1.0/?method=getQuote&format=text&language=ru'
db='db.uple'
contain='Тренды твиттера'
start='#'
stop='<'
indent=20

auth=tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_key,access_secret)
api=tweepy.API(auth)

def get(src):
	urlretrieve(src,db)
	return codecs.open(db,'r','utf-8').read()

def tag():
	text=get(url)
	text=text[text.find(contain)+indent:]
	text=text[text.find(start)+1:]
	return text[:text.find(stop)]

def cont():
	f=True
	a=tag()
	while f:
		text=get(adr)+'\n#'+a
		if len(text)<=140:
			f=False
	return text

# отправка текстового твита
api.update_status(cont())

# получение логина и имени юзера | print(api.me().screen_name, api.me().name)
# фоловим другого юзера | api.get_user('muzhig').follow()