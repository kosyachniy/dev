import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2' #чтобы не было предупреждений TensorFlow об неэффективном использовании

import math
import numpy as np
import tensorflow as tf

compilation = str(2) #набор данных
countcat = 1 #количество выходов
fault = 0.41 #1: 0.41 2: 9146 #с какой погрешностью нужен ответ

#Данные
with open('data/' + compilation + '/table.csv', 'r') as f:
	xx = np.loadtxt(f, delimiter=',', skiprows=1)
with open('data/' + compilation + '/table.csv', 'r') as f:
	yy = np.loadtxt(f, delimiter=',', skiprows=1).T[0].T

for i in range(len(xx)):
	xx[i][0] = 1
yy = np.array([[float(i)] for i in yy])

#Уменьшаем разряд параметров, чтобы при обучении нейронов не выходили громадные ошибки (с каждым разом увеличиваясь)
discharge = 0
for i in xx:
	for j in i[1:]:
		print(j)
		dis = int(math.log(j, 10)) + 1 if j != 0 else 0
		if dis > discharge:
			discharge = dis

discharge -= 1

for i in range(len(xx)):
	for j in range(1, len(xx[0])):
		xx[i][j] /= 10 ** discharge

#Объявляем входное значение x, вес w, какое значение должны получить y
x = tf.placeholder(tf.float32, shape=(len(xx[0]),))
y = tf.placeholder(tf.float32, shape=(1,))
w = tf.Variable(tf.zeros([1, len(xx[0])]))

#Получаем выходное значение
y2 = tf.multiply(x, w)

#Рассчитываем ошибку выходных данных
loss = tf.reduce_mean(tf.square(y2-y))
optimizer = tf.train.GradientDescentOptimizer(0.005).minimize(loss)

#Запуск обучения
with tf.Session() as session:
	tf.global_variables_initializer().run()

	iteration = 0
	while True: #for j in range(3):
		iteration += 1
		print('Iteration №{}'.format(iteration))

		err = 0
		for i in range(len(xx)):
			data = {x: xx[i:(i+1)][0], y: yy[i:(i+1)][0]}
			_, error = session.run([optimizer, loss], feed_dict=data)

			#print("ошибка: %f" % (error, ))
			if error > err: err = error
		
		print('ошибка: %f' % (err, ))
		if err < fault: break

	iii = session.run(w)[0]

for i in range(countcat, len(iii)):
	iii[i] /= 10 ** discharge

#Сохранение весов
np.savetxt('data/' + compilation + '/weights.csv', iii, delimiter=',')
print(iii)

#Рассчёт прогноза
while True:
	x = [1] + [float(i) for i in input().split()]
	print(sum([x[i] * iii[i] for i in range(len(x))]))