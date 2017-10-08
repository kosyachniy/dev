import math, pylab
from matplotlib import mlab

#Описание функции
def func(x):
	y = math.sin(x)
	return y

#Начало, конец и шаг
xmin = -10.0
xmax = 10.0
dx = 0.01

#Значения
xlist = mlab.frange(xmin, xmax, dx)
ylist = [func(x) for x in xlist]

#Строим график
pylab.plot(xlist, ylist)
pylab.show()
pylab.savefig('1.png', format='png', dpi=150)