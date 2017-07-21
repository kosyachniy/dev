import numpy as np
import tensorflow as tf

#Данные
xx=np.array([[62.0,1.0,18.0],[76.0,1.0,48.0],[70.0,0.0,44.0],[33.0,0.0,11.182]])
yy=np.array([[182.0],[170.0],[162.0],[148.0]])

#Объявляем входное значение x, вес w, какое значение должны получить y
x = tf.placeholder(tf.float32, shape=(3,))
y = tf.placeholder(tf.float32, shape=(1,))
w = tf.Variable(tf.zeros([1, 3]))
b = tf.Variable(tf.zeros([1]))

#Получаем выходное значение
#y2=tf.nn.softmax(tf.matmul(x, w)+b)
y2 = tf.add(tf.multiply(x, w), b)

#Рассчитываем ошибку выходных данных
loss = tf.reduce_mean(tf.square(y2-y))
optimizer = tf.train.GradientDescentOptimizer(0.05).minimize(loss)

#Запуск обучения
with tf.Session() as session:
	tf.global_variables_initializer().run()
	for i in range(len(xx)):
		feed_dict={x: xx[i:(i+1)][0], y: yy[i:(i+1)][0]}
		_, l = session.run([optimizer, loss], feed_dict=feed_dict)
		print("ошибка: %f" % (l, ))
	ii=[float(session.run(b))]
	for i in session.run(w)[0]:
		ii.append(float(i))
	
	print(ii)
	su=ii[0]
	for i in ii[1:]:
		su+=i*int(input())
	print(su)