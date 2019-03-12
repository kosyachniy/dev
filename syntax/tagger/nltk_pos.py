def tagger(text):
	from nltk import word_tokenize, pos_tag

	tagged = []
	for el in pos_tag(word_tokenize(text)):
		lemma = el[0]

		tagged.append('{}_{}'.format(lemma, el[1]))

	return tagged