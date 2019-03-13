import matplotlib.pyplot as plt


# Данные

dataset = [
	[10, 17, 24, 16, 22],
	[12, 14, 21, 13, 17],
]

# Настройки

plt.grid(True)

# Построить

plt.boxplot(dataset)
plt.show()