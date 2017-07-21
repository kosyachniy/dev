import tensorflow as tf
import numpy as np

#Данные
#xx=np.array([[1,0.3],[0.4,0.5],[0.7,0.8]])
#yy=np.array([[1,0],[1,0],[0,1]])

xx=np.array([1.0,0.4,0.7])
yy=np.array([1.0,1.0,0.0])

#Объявляем входное значение x, вес w, какое значение должны получить y
x=tf.placeholder(tf.float32, shape=(3,))
y=tf.placeholder(tf.float32, shape=(3,))
#w=tf.Variable(tf.zeros([2, 2])) #2, 2
#b=tf.Variable(tf.zeros([2]))
w=tf.Variable(initial_value=0.0, dtype=tf.float32)
b=tf.Variable(initial_value=0.0, dtype=tf.float32)


#Получаем выходное значение
#y2=tf.nn.softmax(tf.matmul(x, w)+b)
y2=tf.add(tf.multiply(x, w), b)

#Рассчитываем ошибку выходных данных
loss=tf.reduce_mean(tf.square(y-y2))

print('--------------------')

#Запуск обучения
optimizer=tf.train.GradientDescentOptimizer(0.025).minimize(loss)

with tf.Session() as session:
	tf.global_variables_initializer().run()
	for i in range(3):
		feed_dict={x:xx[i], y:yy[i]}
		_, l=session.run([optimizer, loss], feed_dict=feed_dict)
		print("ошибка: %f" % (l, ))
		print("a = %f, b = %f" % (w.eval(), b.eval()))

'''
init=tf.global_variables_initializer()
sess=tf.Session()
sess.run(init)

for i in range(100):
	sess.run(train_step)
	print(sess.run(y2))
'''