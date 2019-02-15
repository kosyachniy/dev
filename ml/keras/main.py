import sys

import numpy as np
from keras.models import Sequential
from keras.layers import Dense


def nn(name, outs=1, epochs=10):
	# Данные

	dataset = np.loadtxt('../data/{}/train.csv'.format(name), delimiter=',', skiprows=1)

	x_train = dataset[:, outs:]
	y_train = dataset[:, :outs]

	dataset = np.loadtxt('../data/{}/test.csv'.format(name), delimiter=',', skiprows=1)

	x_test = dataset[:, outs:]
	y_test = dataset[:, :outs]

	# Нормализация

	el = [i for i in x_train.reshape(1, -1)[0] if i>1]
	dis = int(max(np.log10(el))) + 1 if el else 0
	x_train = np.array([[j/10**dis for j in i] for i in x_train])
	x_test = np.array([[j/10**dis for j in i] for i in x_test])
	# y_train = np.array([[j/10**dis for j in i] for i in y_train])
	# y_test = np.array([[j/10**dis for j in i] for i in y_test])

	# Построение модели

	model = Sequential()
	model.add(Dense(outs, activation='sigmoid', input_shape=(x_train.shape[1],)))

	model.compile(optimizer='sgd', loss='categorical_crossentropy', metrics=['accuracy'])

	# Обучение

	history = model.fit(x=x_train, y=y_train, epochs=epochs, verbose=1, validation_data=(x_test, y_test))

	# Проверка на тестовой выборке

	score = model.evaluate(x_test, y_test, verbose=0)
	print(score)

	return model, history


if __name__ == '__main__':
	name = sys.argv[1]
	outs = int(sys.argv[2]) if len(sys.argv) >= 3 else 1
	epochs = int(sys.argv[3]) if len(sys.argv) >= 4 else 10

	model, history = nn(name, outs, epochs)

	# Сохранение весов

	model.save('../data/{}/model.txt'.format(name))

	# Прогноз

	while True:
		x = np.array([1] + list(map(float, input().split()))).reshape((outs, -1))
		print(model.predict(x))