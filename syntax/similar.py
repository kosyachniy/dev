from re import match
from pymorphy2 import MorphAnalyzer
from gensim.models import KeyedVectors

morph = MorphAnalyzer()
model = KeyedVectors.load_word2vec_format('araneum_upos_skipgram_600_2_2017.bin', binary=True)

vocab = model.vocab.keys()
def speach(x):
	for i in vocab:
		if match(x, i):
			return i
	return None

while True:
	plus = [morph.parse(i)[0].normal_form + '_' for i in input('+: ').split()]
	minus = [morph.parse(i)[0].normal_form + '_' for i in input('-: ').split()]
	#print(plus, minus)

	try:
		plus = [speach(i) for i in plus]
		minus = [speach(i) for i in minus]
		#print(plus, minus)
	except:
		print('Не найдено слово!')
	else:
		x = model.most_similar(positive=plus, negative=minus)
		print('', *['%s (%d%%)' % i for i in x], sep='\n')

		print('-' * 100)