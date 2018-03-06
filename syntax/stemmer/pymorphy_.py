from pymorphy2 import MorphAnalyzer
m = MorphAnalyzer()

for i in m.parse('играющий'):
	print(dir(i))
	print(i.normal_form)

for i in m.parse('пустынных'):
	print(dir(i))
	print(i.normal_form)