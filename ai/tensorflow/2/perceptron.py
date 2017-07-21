import tensorflow as tf
import numpy as np

#Данные
xx=np.array([[1,0.3],[0.4,0.5],[0.7,0.8]])
yy=np.array([[1,0],[1,0],[0,1]])

#Объявляем входное значение x, вес w, какое значение должны получить y
x=tf.placeholder(tf.float32, [None, 2]) #, 1
y=tf.placeholder(tf.float32, [None, 2])
w=tf.Variable(tf.zeros([2, 2]))
b=tf.Variable(tf.zeros([2]))

#Получаем выходное значение
y2=tf.nn.softmax(tf.matmul(x, w)+b)

#Рассчитываем ошибку выходных данных
loss=-tf.reduce_mean(y*tf.log(y2))*1000.0

print('--------------------')

#Запуск обучения
train_step=tf.train.GradientDescentOptimizer(0.005).minimize(loss)
init=tf.global_variables_initializer()
sess=tf.Session()
sess.run(init)

for i in range(100):
	sess.run(train_step)
	print(sess.run(y2))