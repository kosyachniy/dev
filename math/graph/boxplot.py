import matplotlib.pyplot as plt
import numpy as np

z1 = [10, 17, 24, 16, 22]
z2 = [12, 14, 21, 13, 17]

plt.boxplot([z1, z2])
#plt.title('Название')
plt.grid(True)

plt.show()