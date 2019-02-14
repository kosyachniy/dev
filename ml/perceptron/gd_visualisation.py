import sys

import numpy as np
import matplotlib.pyplot as plt


OUTS = 1
FAULT = 0.01
COUNT = 100


def perceptron(name, outs=OUTS, fault=FAULT):
	# Данные

	dataset = np.loadtxt('../data/{}/train.csv'.format(name), delimiter=',', skiprows=1)

	x = np.hstack((np.ones((dataset.shape[0], 1)), dataset[:, outs:]))
	y = dataset[:, :outs]

	# Нормализация
	
	el = [i for i in x.reshape(1, -1)[0] if i>1]
	dis = int(max(np.log10(el))) + 1 if el else 1
	x = np.array([[j/10**dis for j in i] for i in x])

	# Рассчёт весов

	def antigradient(y):
		w = np.zeros((x.shape[1], 1))
		iteration = 0
		history = []

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

			history.append(error_max)
			print('№{}: {}'.format(iteration, error_max)) #

			if error_max < fault:
				break

		return w, history

	w = np.zeros(shape=(y.shape[1], x.shape[1]))
	history = []

	for i, el in enumerate(y.T.reshape(-1, y.shape[0], 1)):
		w_re, history_re = antigradient(el[:, 0])
		w[i] = w_re.T[0]
		history.append(history_re)

	w = w.T

	# Учёт нормализации

	w = np.array([[j/10**dis for j in i] for i in w])

	#

	return w, history


if __name__ == '__main__':
	name = sys.argv[1]
	outs = int(sys.argv[2]) if len(sys.argv) >= 3 else OUTS
	fault = float(sys.argv[3]) if len(sys.argv) >= 4 else FAULT

	w, history = perceptron(name, outs, fault)

	# Сохранение весов

	print(w) #
	np.savetxt('../data/{}/weights.csv'.format(name), w, delimiter=',')

	# Визуализация

	for i in history:
		# step = len(i) // COUNT
		y = i # i[::step]
		x = range(1, len(y)+1) # list(map(lambda j: j*step, range(1, len(y)+1)))

		plt.plot(x, y)

	plt.show()

	# Прогноз

	while True:
		x = np.array([1] + list(map(float, input().split()))).reshape((outs, -1))
		print(x.dot(w).sum(axis=0))