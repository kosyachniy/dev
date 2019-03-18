import sys

import numpy as np
from scipy.misc import derivative


OUTS = 1
FAULT = 0.01

# Сигмоида 
def nonlin(x,deriv=False):
	if(deriv==True):
		return x*(1-x) # f(x)*(1-f(x))
	return 1/(1+np.exp(-x))


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

	def backpropagation(y):
		w = np.zeros((x.shape[1], 1))
		iteration = 0

		def gradient(f, x):
			return derivative(f, x, 1e-6)

		while True: # for iteration in range(1, 51):
			iteration += 1
			error_max = 0

			for i in range(x.shape[0]):
				f1 = nonlin(x[i].dot(w).sum())
				error = y[i] - f1

				# print(error)
				error_max = max(error, error_max)

				# print('Error', error_max, error)

				antigrad = nonlin(f1, True) # -1 * gradient(f, w)

				# print('-∇ = {}'.format(antigrad)) #

				delta = error * antigrad

				for j in range(x.shape[1]):
					w[j] += delta * x[i][j]
					# print('Δw{} = {}'.format(j, delta))

			print('№{}: {}'.format(iteration, error_max)) #

			if error_max < fault:
				break

		return w

	w = np.hstack([backpropagation(i[:, 0]) for i in y.T.reshape(-1, y.shape[0], 1)])

	# Учёт нормализации
	
	w = np.array([[j/10**dis for j in i] for i in w])

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