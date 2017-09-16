import numpy as np
#import random

act = lambda xe, we: sum([xe[i] * we[i] for i in range(len(xe))])

with open('data.csv', 'r') as f:
	x = np.loadtxt(f, delimiter=',', skiprows=1)
with open('data.csv', 'r') as f:
	y = np.loadtxt(f, delimiter=',', skiprows=1).T[0].T

for i in range(len(x)):
	x[i][0] = 1
w = [0 for j in range(len(x))] #random

print(x)
print(y)
print(w)

for iteration in range(100):
	print('Iteration №{}'.format(iteration+1))

	for i in range(len(x)):
		error = (y[i] - act(x[i], w))

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
		print('YES ({}%)'.format(int(round(s*100))))
	else:
		print('NO ({}%)'.format(int(round((1-s)*100))))