from func import *

x=input()
api.get_user(x).follow()
y=api.show_friendship(source_screen_name=x,target_screen_name='kosyachniy')[0]
print(y.following,y.followed_by)
#print(api.followers(x)[0].followers_count)