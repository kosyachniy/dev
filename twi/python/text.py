import tweepy, sys, os, ssl, chardet
if sys.version_info[0]>=3:
	from urllib.request import urlretrieve, urlopen
else:
	from urllib import urlretrieve, urlopen
sys.path.append('../../site')
from open import get

consumer_key='8Y2o5PjasQkVmvoxVQBLyVs4F'
consumer_secret='2r4KPBm8kCcKsNrwkzSQRH4IkDqbxhVrgVcAmvfoyfXbZUNm1L'
access_key='3110781773-4I27iEchYIxqZmIQOgt18b2ehZUHkdEpWKRPuRO'
access_secret='OZj9w6TRUQoeVCgk3pShYOTFWasvSx3ebgOXn6lJQyngy'
'''
consumer_key='jARMeUTgjWhDSWOSbs0pfQYz4'
consumer_secret='stRnOnA3KRpaCI3hjyJyo0eLedQNflQ4FuvudvXj37mSLX7tPa'
access_key='4100776272-4VpvJNSkyhG9kWXfhRHyI3eTEeBRYRABiIqzusU'
access_secret='RHcdHHf0TyHBxtfxHyRCgmB41r7c6gnVgUHH7SEf1Uqi9'
'''
url='http://t30p.ru/'
adr='http://api.forismatic.com/api/1.0/?method=getQuote&format=text&language=ru'
contain='Тренды твиттера'
start='#'
stop='<'
indent=20

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

def post(text):
	if not text:
		text=cont()

	auth=tweepy.OAuthHandler(consumer_key,consumer_secret)
	auth.set_access_token(access_key,access_secret)
	api=tweepy.API(auth)

#Отправка текстового твита
	api.update_status(text)

	return text

if __name__=='__main__':
	post('')

#Получение логина и имени юзера | print(api.me().screen_name, api.me().name)
#Фоловим другого юзера | api.get_user('muzhig').follow()