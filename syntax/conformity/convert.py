import json, re
from func import delete, write

from pymorphy2 import MorphAnalyzer
m = MorphAnalyzer()

def convert(file_in='db', file_out='formated', all_speech=False, attribute='text'):
	style = lambda text: re.sub(r'^\s+|\s$', '', re.sub('\s+|[^a-zа-я –-—]', ' ', text.lower())).split() #0-9

	delete(file_out)
	with open('data/'+file_in+'.json', 'r') as file:
		s = json.loads(file.read())

	for i in s:
		a = []
		for j in style(i[attribute]):
			p = m.parse(j)[0] #
			#Только несущие смысл слова
			if all_speech or p.tag.POS in ('NOUN', 'ADJF', 'VERB'):
				a.append(p.normal_form)
		write(a, file_out)

if __name__ == '__main__':
	convert()