from func import *
import time

def lis(user):
	a=list()
	for i in api.followers(user):
		name=i.screen_name
		if name!='kosyachniy' and i.friends_count>=0.6*i.followers_count:
			y=api.show_friendship(source_screen_name=name,target_screen_name='kosyachniy')[0]
			if name not in a and y.following==False and y.followed_by==False:
				a.append(name)
	return a

'''
for i in api.followers('kosyachniy'):
	if i.friends_count>=1000 and i.followers_count>=1000:
		user=i.screen_name
		break
if not user:
	user=api.followers('kosyachniy')[0].screen_name
'''

way=lis(api.followers('kosyachniy')[0].screen_name)

while True:
	name=way[0]
	if len(way)==1:
		way+=lis(api.followers(name)[0].screen_name)
	api.get_user(name).follow()
	print(name)
	del way[0]
	time.sleep(60)