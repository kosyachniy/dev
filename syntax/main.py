from func import *

x = formed(input().split())

'''
x = model.wv[x]
x = model.wv.doesnt_match(x)
x = model.similarity(*x)
x = model.distance(*x)
x = model[x]
x = model.most_similar_to_given(x, formed(input().split())) #('music', ['water', 'sound', 'backpack', 'mouse']) >>> 'sound'
'''

x = model.most_similar_to_given(x, formed(input().split()))

print(x)