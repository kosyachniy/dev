import time

from mystem import tagger as mystem
from morphy import tagger as morphy
from udpipe import tagger as udpipe


text1 = 'пожарище играющий привет пустынных осветлённых'
text2 = 'мама мыла раму'


text = text2.strip()


# pymystem3

start = time.time()

for _ in range(1):
	tag = mystem(text)

print('-'*100)
print(tag)
print('pymystem3', time.time() - start)

# pymorphy2

start = time.time()

for _ in range(1):
	tag = morphy(text)

print('-'*100)
print(tag)
print('pymorphy2', time.time() - start)

# ufal.udpipe

start = time.time()

for _ in range(1):
	tag = udpipe(text)

print('-'*100)
print(tag)
print('ufal.udpipe', time.time() - start)