import snowballstemmer
print(dir(snowballstemmer))
print(snowballstemmer.EnglishStemmer().stemWord("Gregory"))
print(snowballstemmer.RussianStemmer().stemWord("играющий"))
print(snowballstemmer.RussianStemmer().stemWord("пустынных"))