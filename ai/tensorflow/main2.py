import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import math, random
import numpy as np
import tensorflow as tf

compilation = str(2) #набор данных
countcat = 1 #количество выходов
fault = 0.005 #с какой погрешностью нужен ответ
step = 0.05 #шаг

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
		dis = int(math.log(j, 10)) + 1 if j != 0 else 0
		if dis > discharge:
			discharge = dis

discharge -= 1

for i in range(len(xx)):
	for j in range(1, len(xx[0])):
		xx[i][j] /= 10 ** discharge

#Объявляем входное значение x, вес w, какое значение должны получить y
x = tf.placeholder(tf.float32, shape=[None, len(xx[0])])
y = tf.placeholder(tf.float32, shape=[None, 1])
w1 = tf.Variable(tf.random_normal([len(xx[0]), 1])) #zeros

'''
W_h1 = tf.Variable(tf.zeros([len(xx[0]), 128])) #random_normal
W_h2 = tf.Variable(tf.zeros([128, 512]))
h1 = tf.nn.sigmoid(tf.matmul(x, W_h1))
h2 = tf.nn.sigmoid(tf.matmul(W_h1, W_h2))
W_out = tf.Variable(tf.random_normal([512, 1]))
y_ = tf.matmul(h2, W_out)
'''

#Получаем выходное значение
y2 = tf.matmul(x, w1)

#Рассчитываем ошибку выходных данных
loss = tf.reduce_mean(tf.square(y2-y))
train_step = tf.train.GradientDescentOptimizer(step).minimize(loss)
correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y2, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

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
	j = random.randint(0, 2)
	return train_x[str(j)], train_y[j]

#Запуск обучения
with tf.Session() as s:
	s.run(tf.global_variables_initializer())

	for i in range(1000):
		batch_x, batch_y = next_batch(1) #какими порциями передаём обучающие данные
		s.run(train_step, feed_dict={x: batch_x.reshape(1, -1), y:  np.array([batch_y]).reshape(-1, 1)})

		train_accuracy = loss.eval(feed_dict={x: batch_x.reshape(1, -1), y: np.array([batch_y]).reshape(-1, 1)}) #accuracy

		#if i % 100 == 0:
		print('Шаг {0}. Ошибка: {1}'.format(i, train_accuracy))

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