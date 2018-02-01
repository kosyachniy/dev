import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
import numpy as np
from math import ceil, log
import random

compilation = str(2) #набор данных
count_out = 1 #количество выходов
fault = 0.005 #с какой погрешностью нужен ответ
step = 0.05 #шаг

#Данные
with open('data/' + compilation + '/table.csv', 'r') as f:
	xx = np.loadtxt(f, delimiter=',', skiprows=1)
with open('data/' + compilation + '/table.csv', 'r') as f:
	yy = np.loadtxt(f, delimiter=',', skiprows=1).T[0].T

for i in range(len(xx)): xx[i][0] = 1
yy = np.array([[float(i)] for i in yy])

#Уменьшаем разряд параметров, чтобы при обучении нейронов не выходили громадные ошибки (с каждым разом увеличиваясь)
dis = 0
for i in xx:
	for j in i:
		dis = max(ceil(log(j, 10)) if j != 0 else 0, dis) #int(math.log(j, 10)) + 1

xx = np.array([[j / 10 ** dis for j in i] for i in xx])
yy = np.array([[j / 10 ** dis for j in i] for i in yy])
fault /= 10 ** dis

count_in = len(xx[0])
count_train = len(xx)

#Объявляем входное значение x, вес w, какое значение должны получить y
x = tf.placeholder(tf.float32, shape=[None, count_in])
y = tf.placeholder(tf.float32, shape=[None, count_out])
w1 = tf.Variable(tf.random_normal([count_in, count_out])) #zeros

'''
W_h1 = tf.Variable(tf.zeros([count_in, 128])) #random_normal
W_h2 = tf.Variable(tf.zeros([128, 512]))
h1 = tf.nn.sigmoid(tf.matmul(x, W_h1))
h2 = tf.nn.sigmoid(tf.matmul(W_h1, W_h2))
W_out = tf.Variable(tf.random_normal([512, count_out]))
y_ = tf.matmul(h2, W_out)
'''

#Получаем выходное значение
y2 = tf.matmul(x, w1)

#Рассчитываем ошибку выходных данных
loss = tf.reduce_mean(tf.square(y2-y))
train_step = tf.train.GradientDescentOptimizer(step).minimize(loss) #AdamOptimizer
#correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y2, 1))
#accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

train_x = {str(i): np.array(j) for i, j in enumerate(xx)}
train_y = yy.T[0]

#Случайные данные из обучающий выборки (для равномерности, могут повторяться)
def next_batch(count):
	'''
	arr_x = []
	arr_y = []
	for i in range(count):
		j = random.randint(0, 2)
		arr_x.append(train_x[str(j)])
		arr_y.append(train_y[j])
	return np.array(arr_x), np.array(arr_y)
	'''
	j = random.randint(0, count_train-1)
	return train_x[str(j)].reshape(1, -1), np.array([train_y[j]]).reshape(-1, 1)

#Запуск обучения
with tf.Session() as s:
	s.run(tf.global_variables_initializer())

	j = 0
	while True: #for i in range(10000):
		for i in range(count_train*10): #x10
			batch_x, batch_y = next_batch(1) #какими порциями передаём обучающие данные
			s.run(train_step, feed_dict={x: batch_x, y: batch_y})

		train_accuracy = loss.eval(feed_dict={x: batch_x, y: batch_y}) #accuracy

		#if i % 100 == 0:
		j += 1
		print('Шаг {0}. Ошибка: {1}'.format(j, train_accuracy))

		if train_accuracy <= fault: break

	w1 = s.run(w1)

def sigmoid(x):
	return (1 / (1 + np.exp(-x)))

#Сохранение весов
np.savetxt('data/' + compilation + '/weights.csv', w1, delimiter=',')
print(w1)

#Рассчёт прогноза
while True:
	x = np.array([1.] + [float(i) for i in input().split()])
	print(int(round((x@w1)[0])))