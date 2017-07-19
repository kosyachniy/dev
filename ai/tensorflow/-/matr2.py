import tensorflow as tf
sess=tf.Session()

x=tf.constant([[1.0, 2.0, 3.0, 4.0]])
w=tf.Variable([[0.0], [0.0], [0.0], [0.0]])
y=tf.constant([9.0, 8.0, 7.0, 6.0])
#b=tf.Variable([0.0])

#x2=tf.reshape(x, [1, 4])
#w2=tf.reshape(w, [4, 1])

y2=tf.multiply(w, x)

loss=tf.pow(y2-y, 2)

sess.run(tf.global_variables_initializer())
train_step=tf.train.GradientDescentOptimizer(0.005).minimize(loss)
for i in range(100):
	sess.run(train_step)
	print(sess.run(y2))

xx=[float(i) for i in input().split()]
yy=sess.run(y2)
for i in range(len(xx)):
	print(xx[i]*yy[i])