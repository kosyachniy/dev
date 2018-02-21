from func import read
from numpy.linalg import svd
import numpy as np

def latent_semantic(file_in='table'):
	s = [[int(i) for i in j] for j in read(file_in)]

	s = [list(i) for i in np.array(s).T]

	print(len(s), len(s[0]))

	m1, m2, m3 = svd(s)

	print(len(m1), len(m1[0]), len(m3), len(m3[0]))

	#print(*svd(s), sep='\n------------------------------------------------------------------------\n')

	cat = 0
	coord_m3 = []
	for i in m3:
		coord_m3.append(i[cat])
	for coord_m1 in m1:
		'''
		for i in m1:
			coord_m1.append(i[cat])
		'''
		l = 0
		for i in range(len(coord_m3)):
			l += (coord_m1[i] - coord_m3[i]) ** 2
		l = l ** 0.5
		print(l)

if __name__ == '__main__':
	latent_semantic()