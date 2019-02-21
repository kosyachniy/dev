from func import *

while True:
	plus = formed(input('+: ').split())
	minus = formed(input('-: ').split())
	#print(plus, minus)

	#x = model.most_similar(positive=plus, negative=minus)
	x = model.most_similar_cosmul(positive=plus, negative=minus)

	print('', *['%s (%d%%)' % (i[0], i[1] * 100) for i in x], '-' * 100, sep='\n')