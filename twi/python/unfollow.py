from func import *

who='deepinmylife'

def all(me='deepinmylife'):
#Удаление невзаимных
	api=auth(me)
	for i in tweepy.Cursor(api.followers, id='I_Mate_I').items():
		print(i.followed_by)

if __name__=='__main__':
	all(who)