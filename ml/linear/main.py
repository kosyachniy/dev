import sys

import numpy as np


def linear(name):
	# Данные

	dataset = np.loadtxt('../data/{}/table.csv'.format(name), delimiter=',', skiprows=1)

	x = np.hstack((np.ones((dataset.shape[0], 1)), dataset[:, 1:]))
	y = dataset[:, 0]

	# Рассчёт

	w = np.linalg.inv(x.T.dot(x)).dot(x.T).dot(y)

	return w


if __name__ == '__main__':
	name = sys.argv[1]
	w = linear(name)

	# Сохранение весов

	np.savetxt('../data/{}/weights.csv'.format(name), w, delimiter=',')
	print(w) #

	# Рассчёт прогноза

	while True:
		x = np.array([1] + list(map(float, input().split())))
		print(x.dot(w).sum())