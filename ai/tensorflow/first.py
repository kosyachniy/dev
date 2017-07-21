import numpy as np
import tensorflow as tf
#%matplotlib inline
import matplotlib.pyplot as plt

samples = 50 # количество точек
packetSize = 5 # размер пакета 
def f(x): return 2*x-3 # искомая функция
x_0 = -2 # начало интервала
x_l = 2 # конец интервала
sigma = 0.5 # среднеквадратическое отклонение шума

np.random.seed(0) # делаем случайность предсказуемой (чтобы все желающие могли повторить вычисления на этом же наборе данных)
data_x = np.arange(x_0,x_l,(x_l-x_0)/samples) # массив [-2, -1.92, -1.84, ..., 1.92, 2]
np.random.shuffle(data_x) # перемешать, но не взбалтывать
data_y = list(map(f, data_x)) + np.random.normal(0, sigma, samples) # массив значений функции с шумом
print(",".join(list(map(str,data_x[:packetSize])))) # первый пакет иксов
print(",".join(list(map(str,data_y[:packetSize])))) # и первый пакет игреков

tf_data_x = tf.placeholder(tf.float32, shape=(packetSize,)) # узел на который будем подавать аргументы функции
tf_data_y = tf.placeholder(tf.float32, shape=(packetSize,)) # узел на который будем подавать значения функции

weight = tf.Variable(initial_value=0.1, dtype=tf.float32, name="a")
bias = tf.Variable(initial_value=0.0, dtype=tf.float32, name="b")
model = tf.add(tf.multiply(tf_data_x, weight), bias)

loss = tf.reduce_mean(tf.square(model-tf_data_y)) # функция потерь, о ней ниже
optimizer = tf.train.GradientDescentOptimizer(0.5).minimize(loss) # метод оптимизации, о нём тоже ниже

with tf.Session() as session:
    tf.global_variables_initializer().run()
    for i in range(samples//packetSize):
        feed_dict={tf_data_x: data_x[i*packetSize:(i+1)*packetSize], tf_data_y: data_y[i*packetSize:(i+1)*packetSize]}
        _, l = session.run([optimizer, loss], feed_dict=feed_dict) # запускаем оптимизатор и вычисляем "потери"
        print("ошибка: %f" % (l, ))
        print("a = %f, b = %f" % (weight.eval(), bias.eval()))
    plt.plot(data_x, list(map(lambda x: weight.eval()*x+bias.eval(), data_x)), data_x, data_y, 'ro')
