import numpy as np
dataset = np.loadtxt('data.csv', delimiter=',', skiprows=1)
x = np.hstack((np.ones((dataset.shape[0], 1)), dataset[:, 1:]))
y = dataset[:, :1]
w = np.linalg.inv(x.T.dot(x)).dot(x.T).dot(y).reshape((1, -1))
np.savetxt('weights.csv', w, delimiter=',')