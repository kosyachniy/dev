'''
import random
'''

act = lambda xe, we: we[0] + sum([xe[i] * we[i+1] for i in range(len(xe))])

'''
	s=we[0]
	for i in range(len(xe)):
		s += xe[i] * we[i+1]
'''

yr = [1, 1, 0]

x = [[1, 0.3], [0.4, 0.5], [0.7, 0.8]]
w = [0 for j in range(len(x)+1)]

'''
yr = [182, 170, 162, 148]

x1 = [62, 76, 70, 33]
w1 = [random.random() for j in range(2)]
'''

for i in range(len(x)):
	error = (yr[i] - act(x[i], w))

	print('Δw0 =', error)
	w[0] += error

	for j in range(len(x[i])):
		print('Δw%d = %f' % (j+1, x[i][j] * error))
		w[j+1] += x[i][j] * error

	print('-----')

x=[float(i) for i in input().split()]
s=w[0]
for i in range(len(x)):
	s += x[i] * w[i+1]
if s>=0.5:
	print('YES ({}%)'.format(round(s*100)))
else:
	print('NO ({}%)'.format(round((1-s)*100)))