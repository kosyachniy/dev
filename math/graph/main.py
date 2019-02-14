import numpy as np
import matplotlib.pyplot as plt


# Функция

f = lambda x: x**2 + 6*x + 2

# Начало, конец, шаг

xmin = -10.0
xmax = 10.0
delta = 0.01

# Значения

x1 = np.arange(xmin, xmax, delta)
y1 = list(map(f, x1))

x2 = [1, 6, 7, 9, -3]
y2 = [117, 2, 20, -20, 0]

# Сохранить

plt.plot(x1, y1)
plt.plot(x2, y2)
plt.savefig('re.png', format='png', dpi=150)

# Построить

plt.plot(x1, y1)
plt.plot(x2, y2)
plt.show()