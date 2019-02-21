def lemmatize(text):
	from pymorphy2 import MorphAnalyzer
	m = MorphAnalyzer()

	lemma = lambda word: m.parse(word)[0].normal_form

	tagged = [lemma(word) for word in text.split()]

	return tagged