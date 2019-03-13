import matplotlib.pyplot as plt


# Данные

with open('data.txt', 'r') as file:
	y = list(map(int, file.read().split('\n')))

x = [i for i in range(1, len(y) + 1)]

# Настройки

plt.grid(True)

# Сохранить

plt.plot(x, y, 'o')
plt.savefig('dots.png', format='png', dpi=150)

# Построить

plt.plot(x, y, 'o')
plt.show()