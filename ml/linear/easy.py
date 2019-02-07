import numpy as np


DATASET = 1


# Данные

dataset = np.loadtxt('../data/{}/table.csv'.format(DATASET), delimiter=',', skiprows=1)

x = np.hstack((np.ones((dataset.shape[0], 1)), dataset[:, 1:]))
y = dataset[:, 0]

# Рассчёт

w = np.linalg.inv(x.T.dot(x)).dot(x.T).dot(y)

# Сохранение весов

np.savetxt('../data/{}/weights.csv'.format(DATASET), w, delimiter=',')
print(w) #

# Рассчёт прогноза

while True:
	x = np.array([1] + list(map(float, input().split())))
	print(x.dot(w).sum())