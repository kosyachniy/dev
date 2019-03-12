import time

from snowball import stemmer as snowball
from porter import stemmer as porter


text1 = 'пожарище играющий привет пустынных осветлённых'
text2 = 'мама мыла раму'


text = text2.strip()


# snowball

start = time.time()

for _ in range(1):
	tag = snowball(text)

print('-'*100)
print(tag)
print('snowball', time.time() - start)

# porter

start = time.time()

for _ in range(1):
	tag = porter(text)

print('-'*100)
print(tag)
print('porter', time.time() - start)