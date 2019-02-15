import sys

import joblib


name = sys.argv[1]

# Загрузка модели

model = joblib.load('../data/{}/model.txt'.format(name))

# Прогноз

while True:
	x = [list(map(float, input().split())),]
	print(model.predict(x))