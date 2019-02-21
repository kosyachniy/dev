def tagger(text):
	from pymorphy2 import MorphAnalyzer
	m = MorphAnalyzer()

	def pos(word):
		tagged = []

		for el in m.parse(word):
			lemma = el.normal_form
			pos = el.tag.POS

			tagged.append('{}_{}'.format(lemma, pos))

		return tagged[0]

	tagged = [pos(word) for word in text.split()]

	return tagged