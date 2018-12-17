import numpy as np
import tensorflow as tf

#Данные
with open('data.csv', 'r') as f:
	xxx=np.loadtxt(f, delimiter=',', skiprows=1)
with open('data.csv', 'r') as f:
	yyy=np.loadtxt(f, delimiter=',', skiprows=1).T[0].T

xx=xxx.T
for i in range(len(xx[0])):
	xx[0][i]=1
xx=xx.T

qw=[]
for i in yyy:
	qw.append([float(i)])
yy=np.array(qw)

#Объявляем входное значение x, вес w, какое значение должны получить y
x=tf.placeholder(tf.float32, shape=(len(xx[0]),))
y=tf.placeholder(tf.float32, shape=(1,))
w=tf.Variable(tf.zeros([1, len(xx[0])]))

#Получаем выходное значение
y2=tf.multiply(x, w)

#Рассчитываем ошибку выходных данных
loss=tf.reduce_mean(tf.square(y2-y))
optimizer=tf.train.GradientDescentOptimizer(0.05).minimize(loss)

#Запуск обучения
with tf.Session() as session:
	tf.global_variables_initializer().run()
	for i in range(len(xx)):
		feed_dict={x: xx[i:(i+1)][0], y: yy[i:(i+1)][0]}
		_, l = session.run([optimizer, loss], feed_dict=feed_dict)
		print("ошибка: %f" % (l, ))

	iii=session.run(w)[0]
	np.savetxt('weights.csv', iii, delimiter=',')
	print(iii)