import os
import sys
import csv
import json
import random

import re
# from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer
import nltk


CUT_FREQUENCY = True
CUT_POS = False
CUT_STOP_WORDS = True
SPLITTING = False
MIN_SIZE = 50
MAX_SIZE = 300
ALLOWED_POS = ('noun', 'adjf', 'adjs', 'comp', 'verb', 'infn', 'prtf', 'prts', 'grnd')
STOP_WORDS = {'это', 'который', 'ещё', 'лишь', 'пока', 'свой', 'е', 'либо', 'любой', 'подпишись', 'подписаться', 'канал', 'youtube', 'instagram', 'фото', 'фотограффия', 'январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь', 'наш', 'объясняем', 'объяснять', 'window', 'settings', 'components', 'eagleplayer', 'enabled', 'true', 'false', 'templates', 'multiplayer', 'relatedVideosHeight', 'ramblercommentscounter', 'relatedvideosheight', 'scroll', 'год', 'весь', 'также', 'лента', 'ру', 'х', 'р', 'т', 'д', 'v', 'www', 'http', 'https', 'com', 'org', 'utm', 'life', 'news', 'дабла', 'ять'}


# def lemmatize(text):
# 	processed = Mystem().analyze(text)
# 	lemma = lambda word: word['analysis'][0]['lex'].lower().strip()
# 	return set(lemma(word) for word in processed if 'analysis' in word)

def lemmatize(text, cut_speech=CUT_POS):
	m = MorphAnalyzer()

	def lemma(word):
		word = m.parse(word)[0]
		
		# Отсеивание частей речи
		speech = word.tag.POS

		if not cut_speech or (speech and speech.lower() in ALLOWED_POS):
			return word.normal_form

	return set(lemma(word) for word in text.split()) - {None}

def str2set(text, cut_speech=CUT_POS):
	text = re.sub(r'[^a-zA-Zа-яА-Я]', ' ', text)
	return lemmatize(text, cut_speech)

def doc2set(compilation, cut_speech):
	docs = []

	for doc in compilation:
		with open('data/history/{}.json'.format(doc), 'r') as file:
			for row in file:
				cont = json.loads(row.strip())

				print(cont)

				if not cont['body']:
					continue

				processed = str2set(cont['body'])
				if MIN_SIZE <= len(processed) <= MAX_SIZE:
					docs.append(processed)
	
	# random.shuffle(docs)

	return docs

def word_bag(data, frequency=CUT_FREQUENCY, stop=CUT_STOP_WORDS):
	corpus = set()

	for i in data:
		corpus = corpus | i

	# Частотное отсеивание

	if frequency:
		freq = {word: 0 for word in corpus}

		for el in data:
			for word in el:
				freq[word] += 1

		# ? Сделать по нормальному распределению

		counts = freq.values()
		freq_max = max(counts)

		# print(freq)

		for i in freq:
			if freq[i] <= 2: # freq[i] > freq_max * 0.95 or freq[i] < freq_max * 0.2:
				corpus.remove(i)

	# Стоп-слова

	if stop:
		stopwords = set(nltk.corpus.stopwords.words('russian'))
		stopwords = stopwords | STOP_WORDS

		corpus = corpus - stopwords

	#

	freq_corpus = {i: freq[i] for i in corpus}

	return tuple(corpus), freq_corpus

def set2vector(data, corpus):
	return [int(j in data) for j in corpus]

def set2obj(data, corpus):
	objs = []

	for i in range(len(data)):
		objs.append(set2vector(data[i], corpus))

	return objs

def vectorize(compilation, frequency=CUT_FREQUENCY, cut_speech=CUT_POS):
	texts = doc2set(compilation, cut_speech=cut_speech)
	corpus, freq = word_bag(texts, frequency)

	vectors = set2obj(texts, corpus)

	return texts, vectors, corpus, freq

def write(data, compilation, name, sign=','):
	name = 'data/history/{}/{}.csv'.format(compilation, name)

	# Для записи множеств
	if type(data) in (list, tuple) and type(data[0]) in (set, frozenset):
		data = [tuple(i) for i in data]

	# Для записи матриц
	if type(data) not in (list, tuple) or type(data[0]) not in (list, tuple):
		data = [data]

	with open(name, 'w') as file:
		for i in data:
			csv.writer(file, delimiter=sign, quotechar=' ', quoting=csv.QUOTE_MINIMAL).writerow(i)


if __name__ == '__main__':
	name = sys.argv[1]

	compilations = {
		'polytics': (1004504016, 1190104199), #  1004504016, 1046446760, 1088965540, 1093469585, 1118710283, 1136605823, 1140809683, 1190104199, 1229262015
	}

	frequency = (False if sys.argv[2] == 'x' else True) if len(sys.argv) >= 3 else CUT_FREQUENCY
	cut_speech = (False if sys.argv[3] == 'x' else True) if len(sys.argv) >= 4 else CUT_POS

	texts, vectors, corpus, freq = vectorize(compilations[name], frequency, cut_speech)

	write(texts, name, 'texts')
	write(vectors, name, 'vectors')
	write(corpus, name, 'corpus')

	freq = sorted([(freq[i], i) for i in freq], reverse=True)
	print(*freq[:10], sep='\n')
	write(freq, name, 'top')

	# Отображение

	dataset = len(vectors)

	print('\nDataset: {}\nCorpus: {}\n'.format(dataset, len(corpus)))