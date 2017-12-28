import gensim

import gensim.models.keyedvectors as word2vec
#from gensim.models.word2vec import Word2Vec

model = word2vec.KeyedVectors.load_word2vec_format('ruwikiruscorpora_0_300_20.bin', binary=True)
#model = Word2Vec.load_word2vec_format('ruwikiruscorpora_0_300_20.bin', encoding='utf-8')

print(model.wv['computer'])
'''
print(dir(model.most_similar('')))

print(gensim.models.Word2Vec(['python', 'programming', 'language'], min_count=1, size=3))
print(model.Word2Vec(['python', 'programming', 'language'], min_count=1, size=3))

words = ['woman', 'king', 'man']
map(print, [gensim.models.Word2Vec(i, min_count=1, size=1) for i in words])
print(model.most_similar(positive=[words[0]], negative=[words[1]]))
'''