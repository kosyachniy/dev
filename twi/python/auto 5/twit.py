from func import *

def twit(x):
	me=x['Me']
	api=auth(me)

	it=0

	while True:
		s=[i[:-1] for i in open('twit.txt', 'r').readlines()]
		if len(s):
			u=loads(s[0])['text']
			del s[0]
			with open('twit.txt', 'w') as file:
				for i in s:
					print(i, file=file)

			it+=1

			with open('set.txt', 'r') as file:
				q=loads(file.read())['trends']
			d=''
#Дополнительный текст
			if x['Message'] and len(u)+len(x['Message'])<=137:
				d=x['Message']+' '
#Популярные теги
			if q['ru'] not in u and len(u)+len(q['ru'])<=138:
				d+=q['ru']
			if len(u)+len(q['us'])<140:
				d+=' '+q['us']
#Проверка пост - картинка?
			u+=d if u[:13]=='https://t.co/' else '\n'+d

			try:
				api.update_status(u)
				print('Post {}.'.format(it),u)
			except tweepy.error.TweepError:
				print('Ошибка при постинге!')

			time.sleep(150) #40
		else:
			time.sleep(600)