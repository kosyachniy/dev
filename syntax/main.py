# def tag(word='пожар', modelfile='russian-syntagrus-ud-2.3-181115.udpipe'):
# 	from ufal.udpipe import Model, Pipeline
# 	model = Model.load(modelfile)
# 	pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')

# 	processed = pipeline.process(word)

# 	output = [l for l in processed.split('\n') if not l.startswith('#')]

# 	tagged = ['_'.join(w.split('\t')[2:4]) for w in output if w]
# 	return tagged


def tag(word='играющий'):
	import snowballstemmer

	lemma = snowballstemmer.RussianStemmer().stemWord(word)

	return lemma





# def tag(word='пустынных'):
# 	from nltk.stem import PorterStemmer
# 	m = PorterStemmer()

# 	tagged = m.stem(word)

# 	return tagged


# def tag(word='осветлённых'):
# 	import nltk
# 	# nltk.download('stopwords')
# 	# nltk.download('punkt')
# 	nltk.download('averaged_perceptron_tagger')
# 	from nltk.stem import SnowballStemmer
# 	from nltk import word_tokenize, pos_tag
# 	print(pos_tag(word_tokenize(word)))

# 	stemmer = SnowballStemmer('russian')

# 	return stemmer.stem(word)


print(tag(input().strip()))


# import nltk
# print(dir(nltk.tag))