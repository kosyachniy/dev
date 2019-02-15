# Описание
[![Travis CI](https://travis-ci.org/kosyachniy/dev.svg?branch=master)](https://travis-ci.org/kosyachniy/dev/)

Репозиторий содержит базовые реализации алгоритмов и технолгий (веб сервисы, блокчейн, парсеры, сортировки, нейронные сети, многопоточность, обработка фото / аудио, боты в соцсетях и т.д.).

Библиотека написана для личного использования в проектах и по мере обучения пополняется новыми реализациями. Цель - создание наиболее оптимального кода и дальнейшее использование готовых частей библиотеки. В директориях есть MarkDown файлы с описанием кода и списком источников, откуда была взята информация для написания соответствующего кода.

Наиболее интересные части:
1. [``` syntax/parse.py ```](syntax/parse.py) - Парсер синтаксиса с использованием PyMorphy для определения частей речи и чистки «грязного текста»
2. [``` rating ```](rating) - Бинарный алгоритм рейтингирования
3. [``` bot/vk/meesages.py ```](bot/vk/meesages.py) - Выгрузка всех диалогов и чатов с распознанием вложений всех типов и возможность выгрузить все вложения (``` bot/vk/attachments.py ```)
4. [``` template/php-site ```](template/php-site) и [``` template/flask-site ```](template/flask-site) - С нуля написанные веб-сервисы для максимальной оптимизации на любых устройствах (на данный момент используются как шаблоны в 3х работающих сайтах)

## Структура репозитория
Расположение | Описание
---|---
[``` bot ```](bot) | Боты в сетях: Instagram, Telegram, Twitter, ВКонтакте, ...
[``` file ```](file) | Работа с файлами: стандартные, CSV, JSON, XML, ...
[``` db ```](db) | Работа с базами данных: SQLite, MongoDB
[``` ml ```](ml) | Анализ данных, машинное обучение, нейронные сети, ...
[``` server ```](server) | Реализация сервера: POST / GET запросы, Flask, ...
[``` serverless ```](serverless) | Реализация бессерверных технологий: Zeit Now, Flask, ...
[``` trade ```](trade) | Автоматизированные торги на биржах
[``` chatbot ```](chatbot) | Чатботы
[``` markup ```](markup) | Разметка
[``` regular ```](regular) | Регулярные выражения
[``` parse ```](parse) | Парсинг веб-страниц
[``` syntax ```](syntax) | Парсинг естественного языка
[``` testing ```](testing) | Тестирование
[``` style ```](style) | Стили
[``` site ```](site) | Разработка веб-приложений
[``` program ```](program) | Разработка ПК-приложений
[``` sms ```](sms) | Отправка SMS-сообщений на телефон
[``` blockchain ```](blockchain) | Реализация блокчейн
[``` smartcontract ```](smartcontract) | Смартконтракты
[``` image ```](image) | Обработка изображений
[``` audio ```](audio) | Обработка аудио

<br>

# Разработка
## Технологии
Название | Расположение | Дополнительно
---|---|---
Word2Vec | ``` ml/text ``` | [RusVectores](http://rusvectores.org/ru/)
Telethon Update | ``` bot/telegram/user ``` |

## API и библиотеки
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
## Курсы
Язык | Расположение | Уроки | Код
---|---|---|---
HTML + CSS  | ``` style ``` <br> ``` template/php-site ``` <br> ``` template/flask-site ``` | [HTMLBook](http://htmlbook.ru/) |
JS | ``` js ``` | [JavaScript](http://learn.javascript.ru/) |
Python |  | МФТИ & Mail.Ru: [Coursera](https://www.coursera.org/learn/programming-in-python/home/welcome) <br> [YouTube](https://www.youtube.com/watch?list=PL1A2CSdiySGIPxpSlgzsZiWDavYTAx61d&time_continue=3&v=CkIrizsP64c) <br> [PythonWorld](https://pythonworld.ru/samouchitel-python) |
C++ |  | Яндекс & ВШЭ: [Stepik](https://stepik.org/course/363/syllabus) |

## Полезные ссылки
### Python 3
* [Туториалы, примеры](https://pythonworld.ru/)
* [Code style: PEP8](https://pythonworld.ru/osnovy/pep-8-rukovodstvo-po-napisaniyu-koda-na-python.html)
* [Стандартные библиотеки](https://docs.python.org/3/library/)


## Решение
[Онлайн компилятор](http://ideone.com/)

Тип | Сервис
---|---
Олимпиадные задачи | [CodeForces](http://codeforces.com/problemset)
Олимпиады | [Яндекс.Алгоритм](https://academy.yandex.ru/events/algorithm/)<br>[VK Cup](http://codeforces.com/vkcup2017)<br>[Russian Code Cup](http://www.russiancodecup.ru/ru/)<br>[FaceBook Hacker Cup](https://ru.wikipedia.org/wiki/Facebook_Hacker_Cup)<br>[Google Code Jam](https://code.google.com/codejam/)<br>[КРОК](https://www.croc.ru/vacancy/students/detail/61353/)
Конкурсы | [Web Ready](http://www.gotech.vc/)<br>[Список](https://habrahabr.ru/company/ingria_startup/blog/138718/)
Работа | [HeadHunter](https://spb.hh.ru/search/vacancy?text=python&area=2)

<br>

# Основы
## Терминал
Код | Действие
---|---
``` pip freeze > requirements.txt ``` | Получить requerements.txt
``` source tensorflow/bin/activate/ ``` | Запустить TensorFlow
``` jupyter notebook ``` | Запустить блокнот

## Vim
Команда | Описание
---|---
``` :q ``` | Выйти
``` :q! ``` | Выйти и сохранить
``` :wq ``` | Записать и выйти
``` :wq! ``` | Насильно записать и выйти
``` :x ```, ``` :exit ``` | Записать и выйти, если есть изменения
``` :qa ``` | Выйти отовсюду
``` :cq ``` | Закрыть без сохранения, выйти с ошибкой

## Travis CI
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
