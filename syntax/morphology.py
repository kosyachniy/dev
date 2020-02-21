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

person = {
	None: '-',
	'1per': 'первое',
	'2per': 'второе',
	'3per': 'третье',
}

tense = {
	None: '-',
	'past': 'прошедшее',
	'pres': 'настоящее',
	'futr': 'будущее',
}

animacy = {
	None: '-',
	'anim': 'одушевлённое',
	'inan': 'неодушевлённое',
}

aspect = {
	None: '-',
	'perf': 'совершенный',
	'impf': 'несовершенный',
}

involvement = {
	None: '-',
	'incl': 'включённый',
	'excl': 'невключённый',
}

mood = {
	None: '-',
	'impr': 'повелительное',
	'indc': 'изъявительное',
}

transitivity = {
	None: '-',
	'intr': 'непереходный',
	'tran': 'переходный',
}

voice = {
	None: '-',
	'pssv': 'страдательный',
	'actv': 'действительный',
}

OUTPUT = f'''
Часть речи: {pos[lemma.tag.POS]}
Падеж: {case[lemma.tag.case]}
Число: {number[lemma.tag.number]}
Род: {gender[lemma.tag.gender]}
Лицо: {person[lemma.tag.person]}
Время: {tense[lemma.tag.tense]}
Одушевлённость: {animacy[lemma.tag.animacy]}
Вид: {aspect[lemma.tag.aspect]}
Включённость: {involvement[lemma.tag.involvement]}
Наклонение: {mood[lemma.tag.mood]}
Переходность: {transitivity[lemma.tag.transitivity]}
Залог: {voice[lemma.tag.voice]}
'''

# Форма: (личная, ...)
# Разряд: (Личные, Возвратные, Притяжательные, Определительные, Указательные, Вопросительные, Относительные, Неопределенные, Отрицательные)

print(OUTPUT)

# print(dir(lemma.tag))
# lemma.tag.KNOWN_GRAMMEMES
# lemma.tag.cyr_repr