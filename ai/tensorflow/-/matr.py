import tensorflow as tf
sess=tf.Session()

x=tf.constant([1.0, 2.0, 3.0, 4.0])
w=tf.Variable([0.0, 0.0, 0.0, 0.0]) #Коэффициенты только для этого случая, а нужно для всех
y=tf.constant([1.0])
#b=tf.Variable([0.0])

#x2=tf.reshape(x, [1, 4])
#w2=tf.reshape(w, [4, 1])

y2=tf.multiply(w, x) #Не суммирует
'''
suu=0
for i in sess.run(tf.multiply(w, x)):
	suu+=i
y2=tf.Variable([suu])
'''
#y2=tf.nn.softmax(tf.multiply(x, w)+b)

loss=tf.pow(y2-y, 2)
#loss=-tf.reduce_mean(y*tf.log(y2))*1000.0

sess.run(tf.global_variables_initializer())
train_step=tf.train.GradientDescentOptimizer(0.005).minimize(loss)
for i in range(100):
	sess.run(train_step)
	print(sess.run(y2))

#Не степень верности овтета, а выводит сам ответ
xx=[float(i) for i in input().split()]
yy=sess.run(y2)
su=0
for i in range(len(xx)):
	su+=xx[i]*yy[i]
print(round(su))