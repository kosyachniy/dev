def tagger(text):
	from pymystem3 import Mystem
	m = Mystem()

	processed = m.analyze(text)

	def pos(word):
		tagged = []

		for el in word['analysis']:
			lemma = el['lex'].lower().strip()
			pos = el['gr'].split(',')[0].split('=')[0].strip()

			tagged.append('{}_{}'.format(lemma, pos))

		return tagged[0]

	tagged = [pos(word) for word in processed if 'analysis' in word]

	return tagged