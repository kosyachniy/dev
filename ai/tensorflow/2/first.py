import numpy as np
import tensorflow as tf

xx=np.array([0.3, 0.5, 0.8])
yy=np.array([1.0, 1.0, 0.0])

x = tf.placeholder(tf.float32, shape=(1,))
y = tf.placeholder(tf.float32, shape=(1,))

w = tf.Variable(initial_value=0.0, dtype=tf.float32)
b = tf.Variable(initial_value=0.0, dtype=tf.float32)
y2 = tf.add(tf.multiply(x, w), b)

loss = tf.reduce_mean(tf.square(y2-y))
optimizer = tf.train.GradientDescentOptimizer(0.05).minimize(loss)

with tf.Session() as session:
    tf.global_variables_initializer().run()
    for i in range(len(xx)):
        feed_dict={x: xx[i:(i+1)], y: yy[i:(i+1)]}
        _, l = session.run([optimizer, loss], feed_dict=feed_dict)
        print("ошибка: %f" % (l, ))
        print("a = %f, b = %f" % (w.eval(), b.eval()))