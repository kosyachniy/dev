def predict(ex):
	return [][ex]

def target(ex):
	return [182 ,170, 162, 148][ex]

examples=[62, 76, 70, 33]

perfect = False
while not perfect:
	perfect = True
	for i in examples:
		if predict(i) != target(i):
			perfect = False
			if predict(i):
				w=w-i
			else:
				w=w+i