def stemmer(text):
	# import snowballstemmer

	# import nltk
	# nltk.download('stopwords')
	# nltk.download('punkt')
	# nltk.download('averaged_perceptron_tagger')

	from nltk.stem import SnowballStemmer

	stemmer = SnowballStemmer('russian')

	return [stemmer.stem(word) for word in text.split()]