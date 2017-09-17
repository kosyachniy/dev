import numpy as np
import math
#import random

compilation = str(2) #набор данных
countcat = 1 #количество выходов
fault = 0.005 #с какой погрешностью нужен ответ

act = lambda xe, we: sum([xe[i] * we[i] for i in range(len(xe))])

#Данные
with open('data/' + compilation + '/table.csv', 'r') as f:
	x = np.loadtxt(f, delimiter=',', skiprows=1).T[countcat-1:].T
for i in range(len(x)):
	x[i][0] = 1

#Уменьшаем разряд параметров, чтобы при обучении нейронов не выходили громадные ошибки (с каждым разом увеличиваясь)
discharge = 0
for i in x:
	for j in i[countcat:]:
		print(j)
		dis = int(math.log(j, 10)) + 1 if j != 0 else 0
		if dis > discharge:
			discharge = dis

for i in range(len(x)):
	for j in range(countcat, len(x[0])):
		x[i][j] /= 10 ** discharge

def neiro(column):
	print('Out №{}'.format(column))

#Данные
	with open('data/' + compilation + '/table.csv', 'r') as f:
		y = np.loadtxt(f, delimiter=',', skiprows=1).T[column].T

	w = [0 for j in range(len(x[0]))] #random

	print(x)
	print(y)
	print(w)

	iteration = 0
	while True: #for iteration in range(1, 21):
		iteration += 1
		print('Iteration №{}'.format(iteration))

		exit = True
		for i in range(len(x)):
			#Сделать ограничение по уменьшению ошибки
			error = y[i] - act(x[i], w)
			print(error)

			if error > fault: exit = False

			for j in range(len(x[i])):
				delta = x[i][j] * error
				print('Δw%d = %f' % (j, delta))
				w[j] += delta

			print('-----')

		if exit: break

	return w

w = []
for i in range(countcat):
	w.append([j / (10 ** discharge) for j in neiro(i)])
	w[len(w)-1][0] *= 10 ** discharge
w = np.array(w).T

#Сохранение весов
np.savetxt('data/' + compilation + '/weights.csv', w, delimiter=',')
print(w)

#Рассчёт прогноза
#Работает для одного выхода (матрица весов размерностью (n x 1))!
while True:
	x = [1] + [float(i) for i in input().split()]
	s = act(x, w)
	print(s)
	'''
	for i in s:
		if i>=0.5:
			print('YES ({}%)'.format(int(round(i*100))))
		else:
			print('NO ({}%)'.format(int(round((1-i)*100))))
	'''