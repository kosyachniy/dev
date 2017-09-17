#TensorFlow

#Присоединение библиотеки ИИ
import tensorflow as tf
sess=tf.Session()

#Объявляем входное значение x, вес w, какое значение должны получить y
x=tf.constant(1.0, name='input')
w=tf.Variable(0.8, name='weight')
y=tf.constant(0.0, name='right')

#Получаем выходное значение
y2=tf.multiply(w, x, name='output')

#Рассчитываем ошибку выходных данных
loss=tf.pow(y2-y, 2, name='loss')

#Делает доступ по веб для просмотра графа
summary_writer=tf.summary.FileWriter('log_simple_graph', sess.graph)

print('--------------------')

#Запуск обучения
sess.run(tf.global_variables_initializer())
train_step=tf.train.GradientDescentOptimizer(0.025).minimize(loss)
for i in range(100):
	sess.run(train_step)
	print(sess.run(y2))