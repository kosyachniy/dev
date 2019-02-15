import sys

import numpy as np
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
import joblib


OUTS = 1


def logistic_regression(name, outs=OUTS):
	# Данные

	dataset = np.loadtxt('../data/{}/train.csv'.format(name), delimiter=',', skiprows=1)

	x = dataset[:, outs:]
	y = dataset[:, :outs]

	# Стандартизация

	x = preprocessing.normalize(x)

	# Рассчёт весов

	model = LogisticRegression()
	model.fit(x, y)

	#

	return model


if __name__ == '__main__':
	name = sys.argv[1]
	outs = int(sys.argv[2]) if len(sys.argv) >= 3 else OUTS

	model = logistic_regression(name, outs)

	# Сохранение модели

	# print(model)
	joblib.dump(model, '../data/{}/model.txt'.format(name))

	# Прогноз

	while True:
		x = [list(map(float, input().split())),]
		print(model.predict(x))