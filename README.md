# Описание
[![Travis CI](https://travis-ci.org/kosyachniy/dev.svg?branch=master)](https://travis-ci.org/kosyachniy/dev/)

Репозиторий содержит базовые реализации алгоритмов и технолгий (веб сервисы, блокчейн, парсеры, сортировки, нейронные сети, многопоточность, обработка фото / аудио, боты в соцсетях и т.д.) на разных языках (в основном Python).

Библиотека написана для личного использования в проектах и по мере обучения пополняется новыми реализациями. Цель - создание наиболее оптимального кода и дальнейшее использование готовых частей библиотеки. В директориях есть MarkDown файлы с описанием кода и списком источников, откуда была взята информация для написания соответствующего кода.

Наиболее интересные части:
1. ``` syntax/parse.py ``` - Парсер синтаксиса с использованием PyMorphy для определения частей речи и чисткой «грязного текста»
2. ``` rating ``` - Бинарный алгоритм рейтингирования
3. ``` bot/vk/meesages.py ``` - Выгрузка абсолютно всех диалогов и чатов с распознанием вложений всех типов и возможность выгрузить все вложения (``` bot/vk/attachments.py ```)
4. ``` template/php-site ``` и ``` template/flask-site ``` - С нуля написанные веб-сервисы для максимальной оптимизации на любых устройствах (на данный момент используются как шаблоны в 3х работающих сайтах)

<br>

# Разработка
Технологии
---
Название | Расположение | Дополнительно
---|---|---
Word2Vec | ``` ml/text ``` | [RusVectores](http://rusvectores.org/ru/)
Telethon Update | ``` bot/telegram/user ``` |

API и библиотеки
---
&nbsp; | Python | C++ | PHP
---|---|---|---
GUI | [PyQt](http://pyqt.sourceforge.net/Docs/PyQt5/) |  |
ИИ | [TensorFlow](https://www.tensorflow.org/api_docs/python/)<br>[GitHub](https://github.com/tensorflow/tensorflow) |  |
ВКонтакте | [VK](https://vk.com/dev/methods)<br>[GitHub](https://github.com/python273/vk_api) |  |
Telegram | [GitHub](https://github.com/eternnoir/pyTelegramBotAPI) |  |
Twitter | [TweePy](http://docs.tweepy.org/en/v3.5.0/api.html)<br>[GitHub](https://github.com/tweepy/tweepy) |  |
InstaGram |  |  |
Steam | [Steam](http://steam.readthedocs.io/en/latest/user_guide.html)<br>[GitHub](https://github.com/ValvePython/steam) |  |

<br>

# Обучение
Курсы
---
Предмет | Расположение | Уроки | Код
---|---|---|---
Анализ синтаксиса | ``` syntax ``` | [НКРЯ](http://www.ruscorpora.ru/)<br>[OpenCorpora](http://opencorpora.org/?page=downloads)<br>[RusVectores](http://rusvectores.org/ru/calculator/)<br>[RDT](https://nlpub.ru/Russian_Distributional_Thesaurus) |
HTML / CSS  | ``` style ``` <br> ``` template/php-site ``` <br> ``` template/flask-site ``` | [HTMLBook](http://htmlbook.ru/) |
JS | ``` js ``` | [JavaScript](http://learn.javascript.ru/) |
Python |  | МФТИ & Mail.Ru: [Coursera](https://www.coursera.org/learn/programming-in-python/home/welcome) <br> [YouTube](https://www.youtube.com/watch?list=PL1A2CSdiySGIPxpSlgzsZiWDavYTAx61d&time_continue=3&v=CkIrizsP64c) <br> [PythonWorld](https://pythonworld.ru/samouchitel-python) |
C++ |  | Яндекс & ВШЭ: [Stepik](https://stepik.org/course/363/syllabus) |
GUI | ``` gui ``` | [PythonWorld](https://pythonworld.ru/gui) |


Решение
---
[Онлайн компилятор](http://ideone.com/)

Тип | Сервис
---|---
Олимпиадные задачи | [CodeForces](http://codeforces.com/problemset)
Олимпиады | [Яндекс.Алгоритм](https://academy.yandex.ru/events/algorithm/)<br>[VK Cup](http://codeforces.com/vkcup2017)<br>[Russian Code Cup](http://www.russiancodecup.ru/ru/)<br>[FaceBook Hacker Cup](https://ru.wikipedia.org/wiki/Facebook_Hacker_Cup)<br>[Google Code Jam](https://code.google.com/codejam/)<br>[КРОК](https://www.croc.ru/vacancy/students/detail/61353/)
Конкурсы | [Web Ready](http://www.gotech.vc/)<br>[Список](https://habrahabr.ru/company/ingria_startup/blog/138718/)
Работа | [HeadHunter](https://spb.hh.ru/search/vacancy?text=python&area=2)

<br>

# Основы
Терминал
---
Код | Действие
---|---
``` pip freeze > requirements.txt ``` | Получить requerements.txt
``` source tensorflow/bin/activate/ ``` | Запустить TensorFlow
``` jupyter notebook ``` | Запустить блокнот

Режимы файлов
---
Режим | Обозначение
---|---
r | Открытие на чтение (является значением по умолчанию).
w | Открытие на запись, содержимое файла удаляется, если файла не существует, создается новый.
x | Открытие на запись, если файла не существует, иначе исключение.
a | Открытие на дозапись, информация добавляется в конец файла.

Приставка | Обозначение
---|---
b | Открытие в двоичном режиме.
t | Открытие в текстовом режиме (является значением по умолчанию).
\+ | Открытие на чтение и запись

MarkDown
---
[Разметка README.md](http://coddism.com/zametki/razmetka_readmemd_v_github)

Код | Действие
---|---
``` <br> ``` | Энтер

Travis CI
---
[Travis CI](https://travis-ci.org/kosyachniy/dev/)

### Python
```
language: python
python:
  - "2.6"
  - "2.7"
  - "3.2"
  - "3.3"
  - "3.4"
  - "3.5"
  - "3.5-dev"
  - "3.6"
  - "3.6-dev"
  - "3.7-dev"
  - "nightly"
cache: pip
install:
  - pip install -r requirements.txt
script:
  - ....py
```
