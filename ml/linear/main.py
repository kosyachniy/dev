import sys

import numpy as np


def linear(name, outs=1):
	# Данные

	dataset = np.loadtxt('../data/{}/train.csv'.format(name), delimiter=',', skiprows=1)

	x = np.hstack((np.ones((dataset.shape[0], 1)), dataset[:, outs:]))
	y = dataset[:, :outs]

	# Рассчёт весов

	w = np.linalg.inv(x.T.dot(x)).dot(x.T).dot(y)

	return w


if __name__ == '__main__':
	name = sys.argv[1]
	outs = int(sys.argv[2]) if len(sys.argv) >= 3 else 1

	w = linear(name, outs)

	# Сохранение весов

	print(w) #
	np.savetxt('../data/{}/weights.csv'.format(name), w, delimiter=',')

	# Прогноз

	while True:
		x = np.array([1] + list(map(float, input().split()))).reshape((outs, -1))
		print(x.dot(w).sum(axis=0))