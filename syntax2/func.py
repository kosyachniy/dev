from gensim.models import KeyedVectors
model = KeyedVectors.load_word2vec_format('araneum_upos_skipgram_600_2_2017.bin', binary=True)

#Формирование слова под модель
vocab = model.vocab.keys()
from re import match
from pymorphy2 import MorphAnalyzer
morph = MorphAnalyzer()
def formed(x):
	def search(y):
		for i in vocab:
			if match(y, i):
				return i
		return None

	z = []
	for i in x:
		t = search(morph.parse(i)[0].normal_form + '_')
		if t:
			z.append(t)

	return z