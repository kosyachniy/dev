from func import read
from numpy.linalg import svd
import numpy as np

def latent_semantic(file_in='table'):
	ss = [[int(i) for i in j] for j in read(file_in)]

	s = [list(i) for i in np.array(ss).T]

	print(len(s), len(s[0]))

	m1, m2, m3 = svd(s)

	print(len(m1), len(m1[0]), len(m3), len(m3[0]))

	#print(*svd(s), sep='\n------------------------------------------------------------------------\n')

	key_words = read('base')[0]
	key_sentence = read('table')

#Выделение для каждого предложения - ключевого слова
	for cat in range(len(m3)):
		coord_m3 = []
		for i in m3:
			coord_m3.append(i[cat])
		ll = []
		for coord_m1 in m1:
			'''
			for i in m1:
				coord_m1.append(i[cat])
			'''
			l = 0
			for i in range(len(coord_m3)):
				l += (coord_m1[i] - coord_m3[i]) ** 2
			l = l ** 0.5
			ll.append(l) #print(l)
		q = min(ll)

		lll = [key_words[i] for i in range(len(ss)) if ss[cat][i]]
		if len(lll) > 1:
			print(' '.join(lll), '-', key_words[ll.index(q)])


if __name__ == '__main__':
	latent_semantic()