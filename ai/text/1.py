from gensim.models import KeyedVectors #, Word2Vec
#from gensim.models.keyedvectors import KeyedVectors
model = KeyedVectors.load_word2vec_format('ruwikiruscorpora_0_300_20.bin', binary=True)

'''
x = model.wv['мама']
x = model.most_similar(positive=['мама'], topn=1)
x = Word2Vec(['мама'], min_count=1, size=1)
x = model.wv.most_similar(positive=['женщина', 'король'], negative=['мужчина'])
x = model.wv.most_similar_cosmul(positive=['woman', 'king'], negative=['man'])
x = model.wv.doesnt_match("breakfast cereal dinner lunch".split())
x = model.wv.similarity('woman', 'man')
'''
x = model.most_similar(positive=['женщина', 'король'], negative=['мужчина'])

print(x)