from func import *

x = formed(input().split())
print(x)

'''
x = model.wv[x]
x = model.wv.doesnt_match(x)
x = model.similarity(*x)
x = model.distance(*x)
x = model[x]
x = model.most_similar_to_given(x, formed(input().split())) #('music', ['water', 'sound', 'backpack', 'mouse']) >>> 'sound'
'''

'''
while True:
	y = formed(input().split())
	print(y)

	x = model.most_similar_to_given(x, y)
	print(x)
'''

#print(model.most_similar_to_given(x, formed(input().split())))

print(model[input()])