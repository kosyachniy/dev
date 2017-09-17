import math
import pylab
from matplotlib import mlab

def func(x):
	return math.sin(x)
    
#Начало, конец и шаг
xmin = -10.0
xmax = 10.0
dx = 0.01

#Значения по x
xlist = mlab.frange(xmin, xmax, dx)

#Значения по y
ylist = [func(x) for x in xlist]

#Строим график
pylab.plot(xlist, ylist)
pylab.show()