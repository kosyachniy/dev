import time

from mystem import lemmatize as mystem
from morphy import lemmatize as morphy
from udpipe import lemmatize as udpipe


text1 = 'пожарище играющий привет пустынных осветлённых'
text2 = 'мама мыла раму'


text = text2.strip()


# pymystem3

start = time.time()

for _ in range(1):
	lemma = mystem(text)

print('-'*100)
print(lemma)
print('pymystem3', time.time() - start)

# pymorphy2

start = time.time()

for _ in range(1):
	lemma = morphy(text)

print('-'*100)
print(lemma)
print('pymorphy2', time.time() - start)

# ufal.udpipe

start = time.time()

for _ in range(1):
	lemma = udpipe(text)

print('-'*100)
print(lemma)
print('ufal.udpipe', time.time() - start)