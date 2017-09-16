import numpy as np
#import random

act = lambda xe, we: sum([xe.dot(we) for i in range(len(xe))])

with open('data/text-table.csv', 'r') as f:
	x = np.loadtxt(f, delimiter=',', skiprows=1)
with open('data/text-table.csv', 'r') as f:
	y = np.loadtxt(f, delimiter=',', skiprows=1).T[0:7].T #:7

for i in range(len(x)):
	for j in range(7):
		x[i][j] = 1
#x = x.T[6:].T
w = np.zeros((len(x[0]), 7)) #random

print(x)
print(y)
print(w)

for iteration in range(27):
	print('Iteration №{}'.format(iteration+1))

	for i in range(len(x)):
		#Сделать ограничение на числа (ноль, бесконечность)
		#print(len(x), len(x[0]), len(w), len(w[0]))
		error = (y[i] - act(x[i], w))
		print(error)

		for j in range(len(x[i])):
			print('Δw%d = %f' % (j, x[i][j] * error))
			w[j] += x[i][j] * error

		print('-----')

np.savetxt('data/text-weights.csv', w, delimiter=',')
print(w)