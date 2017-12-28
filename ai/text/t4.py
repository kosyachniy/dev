from gensim.models import KeyedVectors

model = KeyedVectors.load_word2vec_format('ruwikiruscorpora_0_300_20.bin', binary=True)
print(model.most_similar(positive=['word'], topn=1))