import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('qt4agg')

tex = '$\\frac{1}{\\sqrt{2\\sqrt{2\\pi}}} \\exp\\left(-\\frac{(x-\\mu)^2}{2\\sigma^2}\\right)$'

### Создание области отрисовки
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.set_axis_off()

### Отрисовка формулы
t = ax.text(0.5, 0.5, tex,
        horizontalalignment='center',
        verticalalignment='center',
        fontsize=20, color='black')
        
### Определение размеров формулы
ax.figure.canvas.draw()
bbox = t.get_window_extent()
print(bbox.width, bbox.height)

# Установка размеров области отрисовки
fig.set_size_inches(bbox.width/80,bbox.height/80) # dpi=80

### Отрисовка или сохранение формулы в файл
#plt.show()
#plt.savefig('test.svg')
plt.savefig('test.png', dpi=300)