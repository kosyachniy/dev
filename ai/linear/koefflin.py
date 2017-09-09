import urllib
from urllib import request
import numpy as np

fname = input()
f = urllib.request.urlopen(fname)
data = np.loadtxt(f, delimiter=',', skiprows=1)
f = urllib.request.urlopen(fname)
y = np.loadtxt(f, delimiter=',', skiprows=1).T[0].T

#y=data.T[0].T
x=data.T
for i in range(len(x[0])):
	x[0][i]=1
x=x.T
re=np.linalg.inv(x.T.dot(x)).dot(x.T)
for i in re.dot(y):
    print(i,end=' ')