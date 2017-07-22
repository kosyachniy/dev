import urllib
from copy import copy
import numpy as np

with open('data.csv', 'r') as f:
	data=np.loadtxt(f, delimiter=',', skiprows=1)
with open('data.csv', 'r') as f:
	y=np.loadtxt(f, delimiter=',', skiprows=1).T[0].T

#y=copy(data).T[0].T
x=data.T
for i in range(len(x[0])):
	x[0][i]=1
x=x.T
re=np.linalg.inv(x.T.dot(x)).dot(x.T)
w=re.dot(y)

print(w)
su=w[0]
for i in w[1:]:
	su+=i*int(input())
print(su)