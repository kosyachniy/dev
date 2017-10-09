from sys import argv
import pylab

def graph(name = 'dots'):
	#Считываем данные
	with open('data.txt', 'r') as file:
		y = file.read().split('\n')
	x = [i for i in range(1, len(y) + 1)]

	#Настройки
	pylab.grid(True)

	#Сохраняем в файл
	pylab.plot(x, y)
	pylab.savefig(name + '.png', format='png', dpi=150)

	#Выводим на экран
	pylab.plot(x, y)
	pylab.show()

if __name__ == '__main__':
	if len(argv) > 1:
		graph(argv[1])
	else:
		graph()