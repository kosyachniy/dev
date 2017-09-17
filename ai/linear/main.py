import urllib
import numpy as np

compilation = str(1) #набор данных
countcat = 1 #количество выходов

#Данные
with open('data/' + compilation + '/table.csv', 'r') as f:
	x = np.loadtxt(f, delimiter=',', skiprows=1)
with open('data/' + compilation + '/table.csv', 'r') as f:
	y = np.loadtxt(f, delimiter=',', skiprows=1).T[0].T

for i in range(len(x)):
	x[i][0] = 1

#Рассчёт
re = np.linalg.inv(x.T.dot(x)).dot(x.T)
w = re.dot(y)

#Сохранение весов
np.savetxt('data/' + compilation + '/weights.csv', w, delimiter=',')
print(w)

#Рассчёт прогноза
while True:
	x = [1] + [float(i) for i in input().split()]
	print(sum([x[i] * w[i] for i in range(len(x))]))