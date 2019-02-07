import sys

import numpy as np


def perceptron(name, outs=1, fault=0.01):
	# Данные

	dataset = np.loadtxt('../data/{}/train.csv'.format(name), delimiter=',', skiprows=1)

	x = np.hstack((np.ones((dataset.shape[0], 1)), dataset[:, outs:]))
	y = dataset[:, :outs]

	# Уменьшение разрядности параметров
	
	el = [i for i in x.reshape(1, -1)[0] if i>1]
	dis = int(max(np.log10(el))) + 1 if el else 0
	x = np.array([[j/10**dis for j in i] for i in x])

	# Рассчёт весов

	def antigradient(y):
		w = np.zeros((dataset.shape[1], 1))

		iteration = 0
		while True: # for iteration in range(1, 51):
			iteration += 1
			error_max = 0

			for i in range(len(x)):
				error = y[i] - x[i].dot(w).sum()

				error_max = max(error, error_max)
				# print('Error', error_max, error)

				for j in range(len(x[i])):
					delta = x[i][j] * error
					w[j] += delta
					# print('Δw{} = {}'.format(j, delta))

			print('№{}: {}'.format(iteration, error_max)) #

			if error_max < fault:
				break

		return w

	w = np.hstack([antigradient(i[:, 0]) for i in y.T.reshape(-1, y.shape[0], 1)])
	w = np.array([[j/10**dis for j in i] for i in w])

	return w


if __name__ == '__main__':
	name = sys.argv[1]
	outs = int(sys.argv[2]) if len(sys.argv) == 3 else 1
	fault = float(sys.argv[3]) if len(sys.argv) == 4 else 0.01

	w = perceptron(name, outs, fault)

	# Сохранение весов

	print(w) #
	np.savetxt('../data/{}/weights.csv'.format(name), w, delimiter=',')

	# Прогноз

	while True:
		x = np.array([1] + list(map(float, input().split()))).reshape((outs, -1))
		print(x.dot(w).sum(axis=0))