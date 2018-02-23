import json, re, os

with open('data/dict.json', 'r') as file:
	dic = json.loads(file.read())

if os.path.exists('data/corpus.json'):
	with open('data/corpus.json', 'r') as file:
		corpus = json.loads(file.read())
	corp = {o for o in j[u] for u in j['word'] for j in corpus[i] for i in corpus}
else:
	corpus = {
		'noun': [],
		'adjective': [],
		'numeral': [],
		'pronoun': [],
		'verb': [],
		'adverb': [],
		'participle': [],
		'transgressive': [],
		'pretext': [],
		'conjunction': [],
		'particle': [],
		'interjection': [],
	}
	corp = set()

'''
noun - существиетльное
adjective - прилагательное
numeral - числительное
pronoun - местоимение
verb - глагол
adverb - наречие
participle - причастие
transgressive - деепрчиастие
pretext - предлог
conjunction - союз
particle - частица
interjection - междометие
'''

for i in dic:
	i = re.sub(r'([а-яa-z])\1+', r'\1\1', i)

	if i not in corp:
		print(corp, '\n\n', i)

		try:
			next_ = input('Добавить в существующее? ')
		except:
			with open('data/corpus.json', 'w') as file:
				print(json.dumps(corpus), file=file)
			print('\n')
			break

		if next_:
			pass
		else:
			part_of_speech = input('Часть речи: ')
			typ = input('Тип слова? ')
			if not typ: typ = 'standart'

			corpus[part_of_speech].append({'word': {typ: [i,]}})
			corp.add(i)