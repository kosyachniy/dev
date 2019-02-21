import nltk
nltk.download('all')
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()

class LSI(object):
	def __init__(self, stopwords, ignorechars, docs):
		self.wdict = {}
		self.dictionary = []
		self.stopwords = stopwords
		#if type(ignorechars) == unicode:
		ignorechars = ignorechars.encode('utf-8')
		self.ignorechars = ignorechars
		for doc in docs: self.add_doc(doc)

	def prepare(self):
		self.build()
		self.calc()

	def dic(self, word, add = False):
		#if type(word) == unicode:
		word = word.encode('utf-8')
		word = word.lower().translate(None, self.ignorechars)
		word = word.decode('utf-8')
		word = stemmer.stem(word)
		if word in self.dictionary: return self.dictionary.index(word)
		else:
			if add:
				self.dictionary.append(word)
				return len(self.dictionary) - 1
			else: return None

	def add_doc(self, doc):
		words = [self.dic(word, True) for word in doc.lower().split()]
		self.docs.append(words)
		for word in words:
			if word in self.stopwords:  continue
			elif word in self.wdict:   self.wdict[word].append(len(self.docs) - 1)
			else:                      self.wdict[word] = [len(self.docs) - 1]

	def build(self):
		self.keys = [k for k in self.wdict.keys() if len(self.wdict[k]) > 0]
		self.keys.sort()
		self.A = zeros([len(self.keys), len(self.docs)])
		for i, k in enumerate(self.keys):
			for d in self.wdict[k]:
				self.A[i,d] += 1

	def calc(self):
		self.U, self.S, self.Vt = svd(self.A)

	def TFIDF(self):
		wordsPerDoc = sum(self.A, axis=0)
		docsPerWord = sum(asarray(self.A > 0, 'i'), axis=1)
		rows, cols = self.A.shape
		for i in range(rows):
			for j in range(cols):
				self.A[i,j] = (self.A[i,j] / wordsPerDoc[j]) * log(float(cols) / docsPerWord[i])

	def dump_src(self):
		self.prepare()
		print('Здесь представлен расчет матрицы ')
		for i, row in enumerate(self.A):
			print(self.dictionary[i], row)

	def print_svd(self):
		self.prepare()
		print('Здесь сингулярные значения')
		print(self.S)
		print('Здесь первые 3 колонки U матрица ')
		for i, row in enumerate(self.U):
			print(self.dictionary[self.keys[i]], row[0:3])
		print('Здесь первые 3 строчки Vt матрица')
		print(-1*self.Vt[0:3, :])

	def find(self, word):
		self.prepare()
		idx = self.dic(word)
		if not idx:
			print('слово невстерчается')
			return []
		if not idx in self.keys:
			print('слово отброшено как не имеющее значения которое через stopwords')
			return []
		idx = self.keys.index(idx)
		print('word --- ', word, '=', self.dictionary[self.keys[idx]], '.\n')
		# получаем координаты слова
		wx, wy = (-1 * self.U[:, 1:3])[idx]
		print('word {}\t{:0.2f}\t{:0.2f}\t{}\n'.format(idx, wx, wy, word))
		arts = []
		xx, yy = -1 * self.Vt[1:3, :]
		for k, v in enumerate(self.docs):
			ax, ay = xx[k], yy[k]
			dx, dy = float(wx - ax), float(wy - ay)
			arts.append((k, v, ax, ay, sqrt(dx * dx + dy * dy)))
		return sorted(arts, key = lambda a: a[4])


docs =[
	"Британская полиция знает о местонахождении основателя WikiLeaks",
	"В суде США США начинается процесс против россиянина, рассылавшего спам",
	"Церемонию вручения Нобелевской премии мира бойкотируют 19 стран",
	"В Великобритании арестован основатель сайта Wikileaks Джулиан Ассандж",
	"Украина игнорирует церемонию вручения Нобелевской премии",
	"Шведский суд отказался рассматривать апелляцию основателя Wikileaks",
	"НАТО и США разработали планы обороны стран Балтии против России",
	"Полиция Великобритании нашла основателя WikiLeaks, но, не арестовала",
	"В Стокгольме и Осло сегодня состоится вручение Нобелевских премий"
]
ignorechars = ''',:'!'''
word = "США"
lsa = LSI([], ignorechars, docs)
lsa.build()
lsa.dump_src()
lsa.calc()
lsa.print_svd()

for res in lsa.find(word):
	print(res[0], res[4], res[1], docs[res[0]])