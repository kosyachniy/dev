import sys

import numpy as np
import time
from sklearn import preprocessing


OUTS = 1
FAULT = 0.01


def perceptron(name, outs=OUTS, fault=FAULT):
	# Данные

	dataset = np.loadtxt('../data/{}/train.csv'.format(name), delimiter=',', skiprows=1)

	x = np.hstack((np.ones((dataset.shape[0], 1)), dataset[:, outs:]))
	y = dataset[:, :outs]

	# Нормализация

	x, norm = preprocessing.normalize(x, return_norm=True)

	# Рассчёт весов

	def backpropagation(y):
		w = np.zeros((x.shape[1], 1))
		iteration = 0

		while True: # for iteration in range(1, 51):
			iteration += 1
			error_max = 0

			for i in range(x.shape[0]):
				error = y[i] - x[i].dot(w).sum()

				error_max = max(error, error_max)
				# print('Error', error_max, error)

				for j in range(x.shape[1]):
					delta = x[i][j] * error
					w[j] += delta
					# print('Δw{} = {}'.format(j, delta))

			print('№{}: {}'.format(iteration, error_max)) #
			time.sleep(1)

			if error_max < fault:
				break

		return w

	w = np.hstack([backpropagation(i[:, 0]) for i in y.T.reshape(-1, y.shape[0], 1)])

	# # Учёт нормализации

	# w /= np.array([norm]).T

	#

	return w


if __name__ == '__main__':
	name = sys.argv[1]
	outs = int(sys.argv[2]) if len(sys.argv) >= 3 else OUTS
	fault = float(sys.argv[3]) if len(sys.argv) >= 4 else FAULT

	w = perceptron(name, outs, fault)

	# Сохранение весов

	print(w) #
	np.savetxt('../data/{}/weights.csv'.format(name), w, delimiter=',')

	# Прогноз

	while True:
		x = np.array([1] + list(map(float, input().split()))).reshape((outs, -1))
		print(x.dot(w).sum(axis=0))