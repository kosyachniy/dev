# Описание
Репозиторий содержит базовые реализации алгоритмов и технолгий (веб сервисы, блокчейн, парсеры, сортировки, нейронные сети, многопоточность, обработка фото / аудио, боты в соцсетях и т.д.).

Библиотека написана для личного использования в проектах и по мере обучения пополняется новыми реализациями. Цель - создание наиболее оптимального кода и дальнейшее использование готовых частей библиотеки. В директориях есть MarkDown файлы с описанием кода и списком источников, откуда была взята информация для написания соответствующего кода.

## Структура репозитория
Расположение | Описание
---|---
[``` bot ```](bot) | Боты в сетях: Instagram, Telegram, Twitter, ВКонтакте, ...
[``` chatbot ```](chatbot) | Чатботы
[``` file ```](file) | Работа с файлами: текстовые, CSV, JSON, XML, ...
[``` db ```](db) | Работа с базами данных: SQLite, MongoDB
[``` ml ```](ml) | Анализ данных, машинное обучение, нейронные сети, ...
[``` syntax ```](syntax) | Парсинг естественного языка, NLP
[``` parse ```](parse) | Парсинг веб-страниц
[``` browser ```](browser) | Программное управление браузером, иммитация пользователя
[``` server ```](server) | Реализация сервера: POST / GET запросы, Flask, ...
[``` serverless ```](serverless) | Реализация бессерверных технологий: Zeit Now, Flask, ...
[``` tls ```](tls) | Найстрока HTTPS шифрования на сервере
[``` markup ```](markup) | Разметка, синтаксис
[``` regular ```](regular) | Регулярные выражения
[``` web ```](web) | WEB-приложение
[``` p2p ```](p2p) | P2P связь: видео, текст, скрин экрана, аудио
[``` interface ```](interface) | Разработка интерфейсов и пользовательских взаимодействий
[``` style ```](style) | Стили, дизайн
[``` media ```](media) | Медиафайлы: шрифты, иконки, значки, звуки
[``` emoji ```](emoji) | Emoji
[``` program ```](program) | Разработка приложений
[``` js ```](js) | JavaScript разработка
[``` python ```](python) | Python разработка
[``` php ```](php) | PHP разработка
[``` sms ```](sms) | Отправка SMS-сообщений на телефон
[``` blockchain ```](blockchain) | Реализация блокчейн
[``` smartcontract ```](smartcontract) | Смартконтракты
[``` image ```](image) | Обработка изображений
[``` upload ```](upload) | Загрузка файлов на сервер с компьютера
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
[``` competition ```](competition) | Хакатоны, бизнес-кейсы и соревнования

### В разработке
Расположение | Описание
---|---
[``` c++ ```](c++) | C++ разработка
[``` deploy ```](deploy) | Развёртывание
[``` mobile ```](mobile) | Мобильные приложения
[``` compile ```](compile) | Компиляция приложений
[``` trade ```](trade) | Автоматизированные торги на биржах
[``` audio ```](audio) | Обработка аудио
[``` testing ```](testing) | Тестирование
[``` corpus ```](corpus) | Корпус слов, словари

<br>

# Ссылки
## Олимпиадные задачи
* [CodeForces](http://codeforces.com/problemset)

## Олимпиады
* [Яндекс.Алгоритм](https://academy.yandex.ru/events/algorithm/)
* [VK Cup](http://codeforces.com/vkcup2017)
* [Russian Code Cup](http://www.russiancodecup.ru/ru/)
* [FaceBook Hacker Cup](https://ru.wikipedia.org/wiki/Facebook_Hacker_Cup)
* [Google Code Jam](https://code.google.com/codejam/)
* [КРОК](https://www.croc.ru/vacancy/students/detail/61353/)

## Хакатоны
* [Russian Hackers](https://russianhackers.org)

## Конкурсы
* [Web Ready](http://www.gotech.vc/)
* [Список](https://habrahabr.ru/company/ingria_startup/blog/138718/)

## Работа
* [HeadHunter](https://spb.hh.ru/search/vacancy?text=python&area=2)

<br>

# Быстрый доступ
## JSON
```
json.dumps(cont, ensure_ascii=False, indent='\t')
```

## GIT
```
git fetch --all
git reset --hard origin/master
git pull origin master
```

## Python
```
env/bin/pip freeze > requirements.txt
```

## Python сервер
```
python -m SimpleHTTPServer 8000
```

```
python3 -m http.server
```

## NGINX
```
sudo nano /etc/nginx/sites-available/<>

sudo ln -s /etc/nginx/sites-available/<> /etc/nginx/sites-enabled

sudo systemctl restart nginx
```

## Let’s Encrypt
```
sudo certbot --nginx
```