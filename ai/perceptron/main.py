'''
import random
'''

act = lambda xe, we: sum([xe[i] * we[i] for i in range(len(xe))])

yr = [1, 1, 0]
x = [[1, 0.3], [0.4, 0.5], [0.7, 0.8]]
w = [0 for j in range(len(x)+1)]

'''
yr = [182, 170, 162, 148]
x1 = [62, 76, 70, 33]
w1 = [random.random() for j in range(2)]
'''

for i in range(len(x)):
	x[i]=[1]+x[i]

for iteration in range(100):
	print('Iteration №{}'.format(iteration+1))

	for i in range(len(x)):
		#x[i]=[1]+x[i]
		error = (yr[i] - act(x[i], w))

		for j in range(len(x[i])):
			print('Δw%d = %f' % (j, x[i][j] * error))
			w[j] += x[i][j] * error

		print('-----')

while True:
	x = [float(i) for i in input().split()]
	s = w[0]
	for i in range(len(x)):
		s += x[i] * w[i+1]
	if s>=0.5:
		print('YES ({}%)'.format(round(s*100)))
	else:
		print('NO ({}%)'.format(round((1-s)*100)))