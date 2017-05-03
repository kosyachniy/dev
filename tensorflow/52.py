#TensorFlow

#Присоединение библиотеки ИИ
import tensorflow as tf
sess=tf.Session()

#Функция нейрона
def f(input):
	#tf.nn.softmax(input)
	#tf.nn.sigmoid(input)
	return input

def loss(output,right):
	error=[]
	for i in range(len(output)):
		error.append(tf.pow(output[i]-right[i],2))
	return error

#Объявляем входное значение x, вес w, какое значение должны получить y
#constant
x=tf.placeholder(tf.float32, [3]) #tf.ones([3]), name='input'
w=tf.Variable(tf.zeros([3]), name='weight') #Случайный
y=tf.placeholder(tf.float32, [3])
b=tf.Variable(0.0, name='bias') #Случайный

#Получаем выходное значение
#multiply
y2=f(tf.matmul(w, x, name='output')) #+b

#Рассчитываем ошибку выходных данных
error=loss(y2,y)

#Делает доступ по веб для просмотра графа
#summary_writer=tf.summary.FileWriter('log_simple_graph', sess.graph)

print('--------------------')

#Запуск обучения
sess.run(tf.initialize_all_variables())
train_step=tf.train.GradientDescentOptimizer(0.025).minimize(loss)
for i in range(100):
	sess.run(train_step)
	print(sess.run(y2))
