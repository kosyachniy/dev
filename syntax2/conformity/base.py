from func import delete, write, read

def base(min_in=0.005, max_in=0.6, file_in='formated', file_out='base'):
	s = read(file_in)
	dictionary = {}
	max_count = 0

	for i in s:
		for j in i:
			if j in dictionary:
				dictionary[j] += 1
				if dictionary[j] > max_count:
					max_count = dictionary[j]
			else:
				dictionary[j] = 1

	#Без частых и редких слов
	dic = []
	for i in dictionary:
		if min_in * max_count <= dictionary[i] <= max_in * max_count:
			dic.append(i)

	delete(file_out)
	write(dic, file_out)

if __name__ == '__main__':
	base()