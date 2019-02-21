from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
 
words = ["game", "gaming", "gamed", "games", 'играть', 'пылесосить', 'игры']
ps = PorterStemmer()
 
for word in words:
    print(ps.stem(word))