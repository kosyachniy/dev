from func import *

def lis(user):
	a=list()
	for i in api.followers(user):
		name=i.screen_name
		if name!='kosyachniy' and i.friends_count>=0.6*i.followers_count:
			y=api.show_friendship(source_screen_name=name,target_screen_name='kosyachniy')[0]
			if name not in a and y.following==False and y.followed_by==False:
				a.append(name)
				print(name)
	return a

b=lis(input())
c=list()
for i in b:
	c+=lis(i)
b+=c

with open('db2.txt','a') as file:
	for i in b:
		print(i,file=file)