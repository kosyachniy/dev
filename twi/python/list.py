from func import *
import time

x=input()
for i in api.followers(x):
	if i.friends_count>=0.6*i.followers_count:
		print(i.followers_count,i.friends_count,i.screen_name)
'''
api.get_user(x).follow()
y=api.show_friendship(source_screen_name=x,target_screen_name='kosyachniy')[0]
print(y.following,y.followed_by)
'''
#time.sleep(60)