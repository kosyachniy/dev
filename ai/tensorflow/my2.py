import numpy as np
import tensorflow as tf

#Данные
xx=np.array([[1.0,0.3],[0.4,0.5],[0.7,0.8]])
yy=np.array([[1.0,0.0],[1.0,0.0],[0.0,1.0]])
#xx=np.array([0.3, 0.5, 0.8])
#yy=np.array([1.0, 1.0, 0.0])

#Объявляем входное значение x, вес w, какое значение должны получить y
x = tf.placeholder(tf.float32, shape=(2,))
y = tf.placeholder(tf.float32, shape=(2,))
w = tf.Variable(tf.zeros([2, 2]))
b = tf.Variable(tf.zeros([2]))

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
        #print(feed_dict)
        _, l = session.run([optimizer, loss], feed_dict=feed_dict)
        print("ошибка: %f" % (l, ))
        #print("a = %f, b = %f" % (w.eval(), b.eval()))
        print(session.run(w))