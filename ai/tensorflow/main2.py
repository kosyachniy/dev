import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import math
import numpy as np
import tensorflow as tf

compilation = str(2) #набор данных
countcat = 1 #количество выходов
fault = 0.41 #1: 0.41 2: 9146 #с какой погрешностью нужен ответ

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
		print(j)
		dis = int(math.log(j, 10)) + 1 if j != 0 else 0
		if dis > discharge:
			discharge = dis

discharge -= 1

for i in range(len(xx)):
	for j in range(1, len(xx[0])):
		xx[i][j] /= 10 ** discharge

'''
for i in range(len(yy)):
	yy[i] /= 10 ** discharge
'''

def read():
	features = {str(i): np.array(j) for i, j in enumerate(xx)}
	labels = yy.T[0]
	return features, labels

def prepare(features, labels, batch_size):
	dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))
	dataset = dataset.shuffle(1000).repeat().batch(batch_size)
	return dataset.make_one_shot_iterator().get_next()

train_x, train_y = read()

my_feature_columns = []
for key in train_x.keys():
	my_feature_columns.append(tf.feature_column.numeric_column(key=key))

classifier = tf.estimator.DNNClassifier(feature_columns=my_feature_columns, hidden_units=[10, 10], n_classes=2,
    optimizer=tf.train.ProximalAdagradOptimizer(learning_rate=0.1, l1_regularization_strength=0.001))

classifier.train(input_fn=lambda: prepare(train_x, train_y, 1), steps=100)


x = tf.placeholder(tf.float32, shape=[None, len(xx[0])])
y = tf.placeholder(tf.float32, shape=[None, 1])

W_h1 = tf.Variable(tf.zeros([len(xx[0]), 10])) #random_normal
W_h2 = tf.Variable(tf.zeros([10, 10]))
h1 = tf.nn.sigmoid(tf.matmul(x, W_h1))
h2 = tf.nn.sigmoid(tf.matmul(W_h1, W_h2))

W_out = tf.Variable(tf.random_normal([10, 1]))
y_ = tf.matmul(h2, W_out)

# cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(y_, y)
#cross_entropy = tf.reduce_sum(- y * tf.log(y_) - (1 - y) * tf.log(1 - y_), 1)
loss = tf.reduce_mean(tf.square(y_-y))
#loss = tf.reduce_mean(cross_entropy)
train_step = tf.train.GradientDescentOptimizer(0.05).minimize(loss)

correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

import random
def next_batch(j):
	i = random.randint(0,2)
	return train_x[str(i)], train_y[i]

# train
with tf.Session() as s:
	s.run(tf.initialize_all_variables())

	for i in range(5000):
		batch_x, batch_y = next_batch(1) #100
		#print(batch_x.reshape(1, -1), np.array([batch_y]).reshape(-1, 1))
		s.run(train_step, feed_dict={x: batch_x.reshape(1, -1), y:  np.array([batch_y]).reshape(-1, 1)})

		if i % 100 == 0:
			train_accuracy = accuracy.eval(feed_dict={x: batch_x.reshape(1, -1), y: np.array([batch_y]).reshape(-1, 1)})
			print('step {0}, training accuracy {1}'.format(i, train_accuracy))

	print(s.run(W_h1), s.run(W_h2), s.run(W_out))
	W_h1 = s.run(W_h1)
	W_h2 = s.run(W_h2)
	W_out = s.run(W_out)

def sigmoid(x):
	return (1 / (1 + np.exp(-x)))

while True:
	x = np.array([float(i) for i in input().split()])
	print(sigmoid(sigmoid(x@W_h1)@W_h2)@W_out)

#eval_result = classifier.evaluate(input_fn=lambda: iris_data.eval_input_fn(test_x, test_y, 1))

#print('\nTest set accuracy: {accuracy:0.3f}\n'.format(**eval_result))

'''
#Объявляем входное значение x, вес w, какое значение должны получить y
x = tf.placeholder(tf.float32, shape=(len(xx[0]),))
y = tf.placeholder(tf.float32, shape=(1,))
w = tf.Variable(tf.zeros([1, len(xx[0])]))

#Получаем выходное значение
y2 = tf.multiply(x, w)

#Рассчитываем ошибку выходных данных
loss = tf.reduce_mean(tf.square(y2-y))
optimizer = tf.train.GradientDescentOptimizer(0.005).minimize(loss) #AdamOptimizer


#Запуск обучения
with tf.Session() as session:
	tf.global_variables_initializer().run()

	iteration = 0
	while True: #for j in range(3):
		iteration += 1
		print('Iteration №{}'.format(iteration))

		err = 0
		for i in range(len(xx)):
			data = {x: xx[i:(i+1)][0], y: yy[i:(i+1)][0]}
			_, error = session.run([optimizer, loss], feed_dict=data)

			#print("ошибка: %f" % (error, ))
			if error > err: err = error
		
		print('ошибка: %f' % (err, ))
		if err < fault: break

	iii = session.run(w)[0]

for i in range(countcat, len(iii)):
	iii[i] /= 10 ** discharge

#Сохранение весов
np.savetxt('data/' + compilation + '/weights.csv', iii, delimiter=',')
print(iii)

#Рассчёт прогноза
while True:
	x = [1] + [float(i) for i in input().split()]
	print(sum([x[i] * iii[i] for i in range(len(x))]))
'''