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