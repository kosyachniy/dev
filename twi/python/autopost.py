from func import *
from urllib.request import unquote

def post(me=''):
	api=auth(me)
	me=api.me().screen_name
	spost=list()

	def tag(place):
		for j in api.trends_place(place)[0]['trends']:
			cont=unquote(j['query'].replace('+',' '))
			if '#' in cont: return cont
		return unquote(api.trends_place(place)[0]['trends'][0])

	def lpost(user):
		ru=tag(23424936)
		us=tag(2352824)
		for i in api.user_timeline(user):
			if not i.retweeted and not i.in_reply_to_user_id and not i.is_quote_status and not i.in_reply_to_user_id and not i.in_reply_to_status_id and i.favorite_count>=10:
				if ru in i.text:
					text=i.text+'\n'+us
				else:
					text=i.text+'\n'+ru+' '+us
				#else: #Проверка пост - картинка?
				#	text=b
				if len(text)<=140: spost.append(text)

	#Автоматический поиск интересных постов по трендам и количеству подписок, ретвитов
	sname=list()
	with open('top.txt','r') as file:
		for i in file:
			sname.append(i[0:-1])

	lpost(sname[0])
	tpost=False

	it=0
	while True:
		it+=1

		while len(spost)==0:
			if len(sname)<=1:
				tpost=True
				print('Закончились твиты!')
				break
			else:
				lpost(sname[1])
				del sname[0]

		if tpost: break

		try:
			api.update_status(spost[0])
			print('Post. {}.'.format(it),sname[0])
		except tweepy.error.TweepError:
			print('Ошибка при постинге!')
		del spost[0]

		time.sleep(40)

if __name__=='__main__':
	post()