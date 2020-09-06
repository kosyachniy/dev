import matplotlib.pyplot as plt


y = [0, 2, 4, 0, 6, 7, 5, 9, 8, 4, 3, 0, 0, 2, 1, 0, 0]
x = list(range(len(y)))
x_lab = ['<1'] + list(map(str, x[1:]))

plt.bar(x, y)
plt.xticks(x, x_lab)
plt.xlabel('Время, мин.')

plt.show()
# plt.savefig('re.png', format='png', dpi=150)