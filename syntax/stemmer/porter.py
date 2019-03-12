def stemmer(text):
	from nltk.stem import PorterStemmer

	stemmer = PorterStemmer()

	return [stemmer.stem(word) for word in text.split()]