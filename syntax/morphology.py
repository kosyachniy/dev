from pymorphy2 import MorphAnalyzer
m = MorphAnalyzer()


word = input() # 'полицейскую'

lemma = m.parse(word)[0]

# lemma.lexeme
# lemma.inflect

pos = {
	None: '-',
	'NOUN': 'существительное',
	'ADJF': 'полное прилагательное',
	'ADJS': 'краткое прилагательное',
	'COMP': 'компаратив',
	'VERB': 'личный глагол',
	'INFN': 'глагол инфинитив',
	'PRTF': 'полное причастие',
	'PRTS': 'краткое причастие',
	'GRND': 'деепричастие',
	'NUMR': 'числительное',
	'ADVB': 'наречие',
	'NPRO': 'местоимение-существительное',
	'PRED': 'предикатив',
	'PREP': 'предлог',
	'CONJ': 'союз',
	'PRCL': 'частица',
	'INTJ': 'междометие',
}

case = {
	None: '-',
	'nomn': 'именительный',
	'gent': 'родительный',
	'datv': 'дательный',
	'accs': 'винительный',
	'ablt': 'творительный',
	'loct': 'предложный',
	'voct': 'звательный', # ?
	'gen2': 'второй родительный (частичный)', # ?
	'acc2': 'второй винительный', # ?
	'loc2': 'второй предложный (местный)', # ?
}

number = {
	None: '-',
	'sing': 'единственное',
	'plur': 'множественное',
}

gender = {
	None: '-',
	'masc': 'мужской',
	'femn': 'женский',
	'neut': 'средний',
	# ? общий род
}

OUTPUT = f'''
Часть речи: {pos[lemma.tag.POS]}
Падеж: {case[lemma.tag.case]}
Число: {number[lemma.tag.number]}
Род: {gender[lemma.tag.gender]}
'''

print(OUTPUT)