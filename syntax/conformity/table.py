from func import delete, read, write

def table(file_text='formated', file_dict='base', file_out='table'):
	text = read(file_text)
	dictionary = read(file_dict)[0]
	delete(file_out)

	for i in text:
		s = [1 if j in i else 0 for j in dictionary]

		#!уравнять объём обучения (количесвто значящих входных и выходных значений)
		#Без пустых предложений
		if 1 in s: #
			write(s, file_out)

if __name__ == '__main__':
	table()