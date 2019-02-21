#Разбивает на слова и символы, строит логические связи и подчинение, определяет роль каждого слова

from pymorphy2 import MorphAnalyzer
from re import sub
#from langdetect import detect

endsigns = '.!?'
opensigns = '(<\[\{'
closesigns = ')>\]\}'
signs = endsigns + '\'":&*—+\-=`'
allsigns = signs + opensigns + closesigns + ',;…\\|/–«»#'
m = MorphAnalyzer()
#m = MorphAnalyzer(lang='uk')

def convert(item):
	if item:
		return str(item).lower()
	else:
		return ''

def morph(text):
#from pymongo import MongoClient
#	MongoDB
	p = m.parse(text)[0]
	return convert(p.normal_form), convert(p.tag.POS), convert(p.tag.gender), convert(p.tag.case), convert(p.tag.number)
#	print(p)
#import subprocess
#import os
#	cmd='echo "'+i.cont+'" | '+os.getcwd()+'/mystem -i'
#	PIPE=subprocess.PIPE
#	p=subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
#	stderr=subprocess.STDOUT, close_fds=True, cwd='/home/')
#	print(bytes(p.stdout.read()).decode('utf8'))

def parse(str):
#Разбиение текста на слова
	str = sub(r'(['+allsigns+'])', r' \1 ', str).split()
	class word:
		def __init__(self, cont='', inf='', speech='', gender='', case='', number='', language=''):
			self.cont = cont
			self.inf = inf
			self.speech = speech
			self.sentence = ''
			self.case = case
			self.number = number
			self.gender = gender
			self.language = language
	text = []
	t = False
	for i in str:
#Объединение знаков
		if i in signs:
			if t:
				text[len(text)-1].cont += i
			else:
				text.append(word(i, i, 'sign'))
				t = True
		else:
			if i in allsigns:
				text.append(word(i, i, 'sign'))
			elif any(c in '0123456789' for c in i):
				text.append(word(i, i, 'numb'))
#Определение граммем (части речи, падежа, рода, числа, ...)
			else:
				text.append(word(i, morph(i)[0], morph(i)[1], morph(i)[2], morph(i)[3], morph(i)[4])) #,detect(i)
			t = False

#Объединение слов в предложения
	class sentence:
		def __init__(self, number=1):
			self.word = []
			self.count = 0
			self.number = number
	num = 0
	mas = [sentence()]
	t = False
	deep = 1
	for i in range(len(text)):
		if text[i].speech != 'sign':
			mas[num].count += 1
		if text[i].cont in opensigns:
			deep += 1
		mas[num].word.append({
			'original': text[i].cont,
			'infinitive': text[i].inf.lower(),
			'change': text[i].cont.lower(),
			'numsp': num+1,
			'speech': text[i].speech,
			'sentence': text[i].sentence,
			'case': text[i].case,
			'number': text[i].number,
			'gender': text[i].gender,
			'language': text[i].language,
			'deep': deep
		})
		if text[i].cont in closesigns:
			deep -= 1
		if (i != len(text)-1) and (any(c in endsigns for c in text[i].cont) or t or (text[i+1].cont in opensigns)):
			if text[i+1].cont in closesigns:
				t = True
			else:
				t = False
				num += 1
				mas.append(sentence(num+1))


#Определение членов предложения (ЗАМЕНИТЬ НЕЙРОНКОЙ)
	for i in mas:
		t = False
		for j in i.word:
			if j['case'] == 'nomn':
				j['sentence'] = 'subject'
				t = True
		if t:
			for j in i.word:
				if j['speech'] in ('verb', 'infn'):
					j['sentence'] = 'predicate'
#Если предложение из одного слова???
		elif i.count == 1:
			for j in i.word:
				if j['speech'] in ('verb', 'infn'):
					j['sentence'] = 'predicate'

	return mas