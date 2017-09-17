import numpy as np
import tensorflow as tf

compilation = str(1) #набор данных
fault = 0.5 #с какой погрешностью нужен ответ

#Данные
with open('data/' + compilation + '/table.csv', 'r') as f:
	xx = np.loadtxt(f, delimiter=',', skiprows=1)
with open('data/' + compilation + '/table.csv', 'r') as f:
	yyy = np.loadtxt(f, delimiter=',', skiprows=1).T[0].T

for i in range(len(xx)):
	xx[i][0] = 1

qw = []
for i in yyy:
	qw.append([float(i)])
yy = np.array(qw)

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
			feed_dict = {x: xx[i:(i+1)][0], y: yy[i:(i+1)][0]}
			_, error = session.run([optimizer, loss], feed_dict=feed_dict)

			#print("ошибка: %f" % (error, ))
			if error > err: err = error
		
		print('ошибка: %f' % (err, ))
		if err < fault: break

	iii = session.run(w)[0]

#Сохранение весов
np.savetxt('data/' + compilation + '/weights.csv', iii, delimiter=',')
print(iii)

#Рассчёт прогноза
while True:
	x = [1] + [float(i) for i in input().split()]
	print(sum([x[i] * iii[i] for i in range(len(x))]))