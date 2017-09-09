import random

act = lambda x, w: x * w[1] + w[0]

yr = [182, 170, 162, 148]

x1 = [62, 76, 70, 33]
w1 = [[random.random() for j in range(2)] for i in range(4)]

for i in range(len(x1)):
	error = (yr[i] - act(x1[i], w1[i]))

	print('Δw1 =', x1[i] * error)
	print('Δw0 =', error)

	w1 += x1[i] * error
	