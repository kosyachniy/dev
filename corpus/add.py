import json, re, os
from pymorphy2 import MorphAnalyzer
m = MorphAnalyzer()

with open('data/dict.json', 'r') as file:
	dic = json.loads(file.read())

if os.path.exists('data/corpus.json'):
	with open('data/corpus.json', 'r') as file:
		corpus = json.loads(file.read())

	corp = set()
	for i in corpus:
		for j in corpus[i]['word']:
			corp.add(j)
else:
	corpus = {}
	corp = set()

'''
noun - существиетльное - NOUN
adjective - прилагательное - ADJF / ADJS
numeral - числительное - NUMR
pronoun - местоимение - NPRO
verb - глагол - VERB
adverb - наречие - ADVB
participle - причастие - PRTF / PRTS
transgressive - деепрчиастие - GRND
pretext - предлог - PREP
conjunction - союз - CONJ
particle - частица - PRCL
interjection - междометие - INTJ
'''

for i in dic:
	i = re.sub(r'([а-яa-z])\1+', r'\1\1', i)

	if i not in corp:
		print(corp, '\n\n', i)

		parser = m.parse(i)

		try:
			next_ = input('Начальная форма (%s)? ' % ' / '.join([i.normal_form for i in parser]))
		except:
			with open('data/corpus.json', 'w') as file:
				print(json.dumps(corpus, ensure_ascii=False, indent=4), file=file)
			print('\n')
			break

		while True:
			if next_ in corpus:
				print(corpus[next_], '\n')
				if not input('Добавить в другое слово?'):
					corpus[next_]['word'][i] = {}
					continue

			part_of_speech = input('Часть речи (%s): ' % ' / '.join([i.tag.POS for i in parser]))
			corpus[next_] = {'word': {i:{}}, 'part_of_speech': part_of_speech}

			if not input('Добавить ещё раз?'):
				break