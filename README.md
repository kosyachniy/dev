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
[``` chatbot ```](chatbot) | Чатботы
[``` file ```](file) | Работа с файлами: стандартные, CSV, JSON, XML, ...
[``` db ```](db) | Работа с базами данных: SQLite, MongoDB
[``` ml ```](ml) | Анализ данных, машинное обучение, нейронные сети, ...
[``` syntax ```](syntax) | Парсинг естественного языка
[``` parse ```](parse) | Парсинг веб-страниц
[``` browser ```](browser) | Программное управление браузером, иммитация пользователя
[``` server ```](server) | Реализация сервера: POST / GET запросы, Flask, ...
[``` serverless ```](serverless) | Реализация бессерверных технологий: Zeit Now, Flask, ...
[``` markup ```](markup) | Разметка, синтаксис
[``` regular ```](regular) | Регулярные выражения
[``` style ```](style) | Стили, дизайн
[``` media ```](media) | Медиафайлы: шрифты, иконки, значки, звуки
[``` site ```](site) | Разработка веб-приложений
[``` program ```](program) | Разработка приложений
[``` js ```](js) | JavaScript разработка
[``` sms ```](sms) | Отправка SMS-сообщений на телефон
[``` blockchain ```](blockchain) | Реализация блокчейн
[``` smartcontract ```](smartcontract) | Смартконтракты
[``` image ```](image) | Обработка изображений
[``` bash ```](bash) | Терминал, BASH команды
[``` git ```](git) | Git команды
[``` algorithm ```](algorithm) | Алгоритмы
[``` editor ```](editor) | WYSIWYG-редакторы
[``` gui ```](gui) | Пользовательский интерфейс
[``` map ```](map) | Работа с картами
[``` math ```](math) | Математика
[``` microcontroller ```](microcontroller) | Программирование микроконтроллеров
[``` template ```](template) | Шаблоны
[``` thread ```](thread) | Многопоточность
[``` time ```](time) | Работа со временем, датами

### В разработке
Расположение | Описание
---|---
[``` c++ ```](c++) | C++ разработка
[``` deploy ```](deploy) | Развёртывание
[``` mobile ```](mobile) | Мобильные приложения
[``` php ```](php) | PHP разработка
[``` python ```](python) | Python разработка
[``` upload ```](upload) | Загрузка файлов на сервер с компьютера
[``` user ```](user) | Авторизация пользователя
[``` compile ```](compile) | Компиляция приложений
[``` trade ```](trade) | Автоматизированные торги на биржах
[``` audio ```](audio) | Обработка аудио
[``` testing ```](testing) | Тестирование
[``` corpus ```](corpus) | Корпус слов, словари

<br>

# Сервисы
Тип | Сервис
---|---
Олимпиадные задачи | [CodeForces](http://codeforces.com/problemset)
Олимпиады | [Яндекс.Алгоритм](https://academy.yandex.ru/events/algorithm/)<br>[VK Cup](http://codeforces.com/vkcup2017)<br>[Russian Code Cup](http://www.russiancodecup.ru/ru/)<br>[FaceBook Hacker Cup](https://ru.wikipedia.org/wiki/Facebook_Hacker_Cup)<br>[Google Code Jam](https://code.google.com/codejam/)<br>[КРОК](https://www.croc.ru/vacancy/students/detail/61353/)
Конкурсы | [Web Ready](http://www.gotech.vc/)<br>[Список](https://habrahabr.ru/company/ingria_startup/blog/138718/)
Работа | [HeadHunter](https://spb.hh.ru/search/vacancy?text=python&area=2)