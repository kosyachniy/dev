# NLP (Natural Language Processing)
## Структура репозитория
Где | Что | Описание
---|---|---
[``` lemmatize/ ```](lemmatize/) | Лемматизация | Приведение к начальной форме
[``` stemmer/ ```](stmmeer/) | Стемминг | Нахождение основы слова
[``` tagger/ ```](tagger/) | Токенизация | Теггинг


## Ресурсы
Нужно? | Что | Ссылка
---|---|---
✔ | Модели и корпуса русских слов | [RusVectores](https://rusvectores.org/ru/models/)
❌ | Токенизатор, тэгер, лемматизатор | [UDPipe](http://ufal.mff.cuni.cz/udpipe), [Скачать](http://ufal.mff.cuni.cz/udpipe/users-manual#universal_dependencies_20_models), [Скачать](http://ufal.mff.cuni.cz/udpipe/models#universal_dependencies_23_models_download), [Скачать](https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-2898#)
❌ | Корпус лемматизированных (морфологически нормализованных) текстов российских СМИ | [GitHub](https://github.com/maxoodf/russian_news_corpus)


##  Источники
### Документация
* [Документация PyMorphy](https://pymorphy2.readthedocs.io/en/latest/user/grammemes.html)
* [Список POS тегов NLTK](https://stackoverflow.com/questions/15388831/what-are-all-possible-pos-tags-of-nltk)

### Принцип
* [Латентно-семантический анализ](https://habr.com/ru/post/110078/)
* [ODS NLP](https://habr.com/ru/company/ods/blog/329410/)
* [Примеры Word2Vec](https://habr.com/ru/post/249215/)
* [Токенизация русского текста](https://habr.com/ru/post/343704/)
* [Визуализация, t-SNE](https://habr.com/ru/company/mailru/blog/426113/)

### Реализация
* [Issue RusVectores Word2Vec](https://github.com/RaRe-Technologies/gensim-data/issues/3)
* [PyMorphy парсер](https://habr.com/ru/post/350802/), [код](https://github.com/sshmakov/RLParser/blob/master/phrases.py)
* [Нейронка для морфологического анализа (POS теггинг)](https://github.com/IlyaGusev/rnnmorph)


## Ключевые фразы (поисковики)
* RusVectores Word2Vec
* NLTK tagger
* pymorphy2 мама мыла раму
* векторизация текста
* нормализация текста
* word2vec python examples
* word2vec классификация