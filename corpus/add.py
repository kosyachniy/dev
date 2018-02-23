import json, re, os

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
			next_ = input('Начальная форма? ')
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

			part_of_speech = input('Часть речи: ')
			corpus[next_] = {'word': {i:{}}, 'part_of_speech': part_of_speech}

			if not input('Добавить ещё раз?'):
				break