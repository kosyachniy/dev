import csv
import matplotlib.pyplot as plt


FAULT = 0.001 # 0.01
# ITERATIONS = 100


def read(name, sign=','):
	with open('data/{}.csv'.format(name), 'r') as file:
		data = list(csv.reader(file, delimiter=sign, quotechar=' '))[1:]
		return list(map(lambda x: list(map(int, x)), data))

def to_dataset(data):
	return [i[1:] for i in data], [i[0] for i in data]

def dispersion(col):
	x_mean = sum(col) / len(col)
	return sum([(x-x_mean)**2 for x in col]) / (len(col) - 1)

def standard_deviation(col):
	return dispersion(col) ** 0.5

def to_z(x_mean, sd, x):
	return (x - x_mean) / sd

def un_z(x_mean, sd, x):
	return x * sd + x_mean

def z_score(col):
	x_mean = sum(col) / len(col)
	sd = standard_deviation(col) * 10 # !
	return x_mean, sd, [to_z(x_mean, sd, x) for x in col]

def z_score_fixed(x_mean, sd, col):
	return [to_z(x_mean, sd, x) for x in col]

def t(m):
	return list(zip(*m))

def x_to_z(x):
	x = [z_score(i) for i in t(x)]
	x_mean, sd, x_new = zip(*x)
	return x_mean, sd, t(x_new)

def x_to_z_fixed(x_mean, sd, x):
	x_t = t(x)
	x = [z_score_fixed(x_mean[i], sd[i], x_t[i]) for i in range(len(x_t))]
	return t(x)

def predict(x, w):
	x_new = [1, *x]
	return sum(x_new[i] * w[i] for i in range(len(w)))

def rmse(x):
	return (sum([(i[0]-i[1])**2 for i in x]) / len(x)) ** 0.5

def calculate_error(y1, y2):
	return y1 - y2
	# return ((y1 - y2) ** 2 / 2) ** 0.5

def fit(x, y):
	w = [0 for _ in range(len(x[0])+1)]

	iteration = 0
	history = []

	while True: # for iteration in range(1, ITERATIONS):
		iteration += 1
		error_max = 0

		for i in range(len(x)):
			y_predict = predict(x[i], w)
			error = calculate_error(y[i], y_predict)
			error_max = max(error_max, error)

			row = [1, *x[i]]
			for j in range(len(w)):
				delta = row[j] * error
				w[j] += delta
				# print('Δw{} = {}'.format(j, delta))

		history.append(error_max)
		# print('№{}: {}'.format(iteration, error_max))

		if error_max < FAULT:
			break

	return w, history


if __name__ == '__main__':
	# Данные для обучения
	train = read('train')
	x, y = to_dataset(train)

	# Нормализация
	x_mean, x_sd, x_norm = x_to_z(x)
	y_mean, y_sd, y_norm = z_score(y)
	# print(x_norm, y_norm, w)

	# Обучение
	w, axis_y = fit(x_norm, y_norm)

	# График обучения
	axis_x = list(range(len(axis_y)))
	plt.plot(axis_x, axis_y)
	plt.show()

	# Прогноз на тестовых данных
	y_pairs = [(y_norm[i], predict(x_norm[i], w)) for i in range(len(x_norm))]
	train_y_unnorm = []
	for i in range(len(y_pairs)):
		y_cor = int(un_z(y_mean, y_sd, y_pairs[i][0]))
		y_pre = int(un_z(y_mean, y_sd, y_pairs[i][1]))
		train_y_unnorm.append((y_cor, y_pre))
		print('Right: {} - Predict: {}'.format(y_cor, y_pre))

	# Метрика прогноза на данных для обучения
	print('RMSE Train: {}'.format(rmse(train_y_unnorm)))

	# Тестовые данные
	test = read('test')
	x, y = to_dataset(test)

	# Нормализация тестовых данных
	x_norm = x_to_z_fixed(x_mean, x_sd, x)
	y_norm = z_score_fixed(y_mean, y_sd, y)

	# Прогноз на тестовых данных
	y_pairs = [(y_norm[i], predict(x_norm[i], w)) for i in range(len(x_norm))]
	test_y_unnorm = []
	for i in range(len(y_pairs)):
		y_cor = int(un_z(y_mean, y_sd, y_pairs[i][0]))
		y_pre = int(un_z(y_mean, y_sd, y_pairs[i][1]))
		test_y_unnorm.append((y_cor, y_pre))
		print('Right: {} - Predict: {}'.format(y_cor, y_pre))

	# Метрика прогноза на тестовых данных
	print('RMSE Test: {}'.format(rmse(test_y_unnorm)))

	# График прогноза
	# fig = plt.figure()
	axis_y = [i[0] for i in train_y_unnorm] + [i[0] for i in test_y_unnorm]
	axis_y_train_predict = [i[1] for i in train_y_unnorm]
	axis_y_test_predict = [i[1] for i in test_y_unnorm]
	axis_x = range(len(axis_y))
	axis_x_train = range(len(axis_y_train_predict))
	axis_x_test = range(len(axis_y_train_predict), len(axis_y))
	plt.plot(axis_x, axis_y)
	plt.plot(axis_x_train, axis_y_train_predict)
	plt.plot(axis_x_test, axis_y_test_predict)
	plt.grid()
	plt.axis((0, len(axis_y)-1, 120, 200))
	plt.show()