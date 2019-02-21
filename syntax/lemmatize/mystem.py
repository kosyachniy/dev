def lemmatize(text):
	from pymystem3 import Mystem
	m = Mystem()

	processed = m.analyze(text)

	lemma = lambda word: word['analysis'][0]['lex'].lower().strip()

	tagged = [lemma(word) for word in processed if 'analysis' in word]

	return tagged