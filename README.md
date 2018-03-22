# Описание
[![Travis CI](https://travis-ci.org/kosyachniy/dev.svg?branch=master)](https://travis-ci.org/kosyachniy/dev/)

Репозиторий содержит базовые реализации алгоритмов и технолгий (веб сервисы, блокчейн, парсеры, сортровки, нейронные сети, многопоточность, обработка фото / аудио, боты в соцсетях и т.д.) на различных языках (в основном Python).
Библиотека написана для личного использования в других собственных проектах и по мере обучения пополняется новыми реализациями. Цель - создание наиболее оптимального кода и дальнейшее использование готовых частей библиотеки. В директориях есть MarkDown файлы с описанием кода и из каких источников была взята информация для написания соответствующего кода.

<br>

# Разработка
Технологии
---
Название | Расположение | Дополнительно
---|---|---
Word2Vec | ``` ai/text ``` | [RusVectores](http://rusvectores.org/ru/)
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
Регулярные выражения | ``` regular ``` | [HabraHabr](https://habrahabr.ru/post/115825/) |
MNIST | ``` ai/tensorflow/mnist ``` | [Google](https://codelabs.developers.google.com/codelabs/cloud-tensorflow-mnist/#0) | [GitHub](https://github.com/martin-gorner/tensorflow-mnist-tutorial)
GUI | ``` gui ``` | [PythonWorld](https://pythonworld.ru/gui) |
HTML / CSS  | ``` template/php/site ``` | [HTMLBook](http://htmlbook.ru/) |
JS | ``` js ``` | [JavaScript](http://learn.javascript.ru/) |
AI / ML / DML | ``` ai/tensorflow ``` | Open Data Science: [ВК](https://vk.com/mlcourse) [HabraHabr](https://habrahabr.ru/company/ods/blog/322626/)<br>ВШЭ & Яндекс: [Coursera](https://www.coursera.org/learn/vvedenie-mashinnoe-obuchenie)<br>[Stepik](https://stepik.org/course/%D0%9D%D0%B5%D0%B9%D1%80%D0%BE%D0%BD%D0%BD%D1%8B%D0%B5-%D1%81%D0%B5%D1%82%D0%B8-401/syllabus)<br>[HabraHabr 1](https://habrahabr.ru/post/312450/)<br>[HabraHabr 2](https://habrahabr.ru/post/313216/) |
Python |  | [PythonWorld](https://pythonworld.ru/samouchitel-python) |
Анализ синтаксиса | ``` syntax ```<br>``` parse/text ``` | [НКРЯ](http://www.ruscorpora.ru/)<br>[OpenCorpora](http://opencorpora.org/?page=downloads)<br>[RusVectores](http://rusvectores.org/ru/calculator/)<br>[RDT](https://nlpub.ru/Russian_Distributional_Thesaurus) |


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
