from func import *
import time

x=input()
for i in api.followers(x):
	print(i.screen_name)
'''
api.get_user(x).follow()
y=api.show_friendship(source_screen_name=x,target_screen_name='kosyachniy')[0]
print(y.following,y.followed_by)
'''
#time.sleep(60)