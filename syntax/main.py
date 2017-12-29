from pymorphy2 import MorphAnalyzer
from gensim.models import KeyedVectors #, Word2Vec

morph = MorphAnalyzer()
model = KeyedVectors.load_word2vec_format('araneum_upos_skipgram_600_2_2017.bin', binary=True)

'''
x = model.wv['мама']
x = model.most_similar(positive=['мама'], topn=1)
x = Word2Vec(['мама'], min_count=1, size=1)
x = model.most_similar(positive=['женщина', 'король'], negative=['мужчина'])
x = model.wv.most_similar(positive=['женщина', 'король'], negative=['мужчина'])
x = model.wv.most_similar_cosmul(positive=['woman', 'king'], negative=['man'])
x = model.wv.doesnt_match("breakfast cereal dinner lunch".split())
x = model.wv.similarity('woman', 'man')
'''

x = input()

x = morph.parse(x)[0].normal_form + '_'
print(x)

vocab = model.vocab.keys()
for i in vocab:
	if x in i:
		x = i
		break
print(x)

#x = model.most_similar(positive=['женщина_NOUN', 'король_NOUN'], negative=['мужчина_NOUN'])
x = model.most_similar(positive=[x], topn=1)

print(x)