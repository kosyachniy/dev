import numpy as np
#import random

countcat=1

act = lambda xe, we: sum([xe[i] * we[i] for i in range(len(xe))])

with open('data/table.csv', 'r') as f:
	x = np.loadtxt(f, delimiter=',', skiprows=1).T[countcat-1:].T
for i in range(len(x)):
	x[i][0] = 1

def neiro(column):
	print('Out №{}'.format(column))

	with open('data/table.csv', 'r') as f:
		y = np.loadtxt(f, delimiter=',', skiprows=1).T[column].T

	w = [0 for j in range(len(x[0]))] #random

	print(x)
	print(y)
	print(w)

	for iteration in range(100):
		print('Iteration №{}'.format(iteration+1))

		for i in range(len(x)):
			#Сделать ограничение по уменьшению ошибки
			error = y[i] - act(x[i], w)
			print(error)

			for j in range(len(x[i])):
				delta = x[i][j] * error
				print('Δw%d = %f' % (j, delta))
				w[j] += delta

			print('-----')

	return w

w = []
for i in range(countcat):
	w.append(neiro(i))
w = np.array(w).T

#Сохранение весов
np.savetxt('data/weights.csv', w, delimiter=',')
print(w)

#Рассчёт прогноза
#Работает для одного выхода (матрица весов размерностью (n x 1))!
while True:
	x = [1] + [float(i) for i in input().split()]
	s = act(x, w)[0] #т.к. один выход
	if s>=0.5:
		print('YES ({}%)'.format(int(round(s*100))))
	else:
		print('NO ({}%)'.format(int(round((1-s)*100))))