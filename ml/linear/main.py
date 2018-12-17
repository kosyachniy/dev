import urllib
import numpy as np

compilation = str(4) #набор данных
countcat = 8 #количество выходов

#Данные
with open('data/' + compilation + '/table.csv', 'r') as f:
	x = np.loadtxt(f, delimiter=',', skiprows=1)
for i in range(len(x)):
	x[i][0] = 1

def neiro(column):
	with open('data/' + compilation + '/table.csv', 'r') as f:
		y = np.loadtxt(f, delimiter=',', skiprows=1).T[column].T

	#Рассчёт
	re = np.linalg.inv(x.T.dot(x)).dot(x.T)
	w = re.dot(y)

	return w

w = []
for i in range(countcat):
	w.append(neiro(i))
w = np.array(w).T

#Сохранение весов
np.savetxt('data/' + compilation + '/weights.csv', w, delimiter=',')
print(w)

#Рассчёт прогноза
while True:
	x = [1] + [float(i) for i in input().split()]
	print(sum([x[i] * w[i] for i in range(len(x))])[0])