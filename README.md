# Описание
Репозиторий содержит базовые реализации алгоритмов и технолгий (веб сервисы, блокчейн, парсеры, сортировки, нейронные сети, многопоточность, обработка фото / аудио, боты в соцсетях и т.д.).

Библиотека написана для личного использования в проектах и по мере обучения пополняется новыми реализациями. Цель - создание наиболее оптимального кода и дальнейшее использование готовых частей библиотеки. В директориях есть MarkDown файлы с описанием кода и списком источников, откуда была взята информация для написания соответствующего кода.

## Структура репозитория
Расположение | Описание
---|---
[``` api ```](api) | Работа с API сервисов (Google, Facebook, Yandex)
[``` docker ```](docker) | Docker контейнеры
[``` vk-miniapps ```](vk-miniapps) | VK Mini Apps
[``` bots ```](bots) | Боты в сетях: Instagram, Telegram, Twitter, ВКонтакте, Facebook, ...
[``` chatbot ```](chatbot) | Чатботы
[``` markup ```](markup) | Разметка, синтаксис: MarkDown, TeX, LaTeX
[``` file ```](file) | Работа с файлами: текстовые, CSV, JSON, XML, ...
[``` db ```](db) | Работа с базами данных: SQLite, MongoDB
[``` ml ```](ml) | Анализ данных, машинное обучение, нейронные сети, ...
[``` syntax ```](syntax) | Парсинг естественного языка, NLP
[``` parse ```](parse) | Парсинг веб-страниц
[``` browser ```](browser) | Программное управление браузером, иммитация пользователя
[``` server ```](server) | Реализация сервера: POST / GET запросы, Flask, ...
[``` serverless ```](serverless) | Реализация бессерверных технологий: Zeit Now, Flask, ...
[``` tls ```](tls) | Найстрока HTTPS шифрования на сервере
[``` regular ```](regular) | Регулярные выражения
[``` web ```](web) | Комплексная разработка Web-приложения
[``` template ```](template) | Шаблоны
[``` p2p ```](p2p) | P2P связь: видео, текст, скрин экрана, аудио
[``` map ```](map) | Работа с картами
[``` pay ```](pay) | Платежи, переводы
[``` gui ```](gui) | Пользовательский интерфейс
[``` interface ```](interface) | Разработка интерфейсов и пользовательских взаимодействий
[``` style ```](style) | UX/UI, стили
[``` media ```](media) | Медиафайлы: шрифты, иконки, значки, звуки
[``` emoji ```](emoji) | Emoji
[``` program ```](program) | Базовые реализации "Hello, world!" на разных языках программирования
[``` oop ```](oop) | Объектно-ориентированное программирование
[``` js ```](js) | JavaScript разработка
[``` python ```](python) | Python разработка
[``` php ```](php) | PHP разработка
[``` sms ```](sms) | Отправка SMS-сообщений
[``` mail ```](mail) | Подписи для почты
[``` crypto ```](crypto) | Работа с криптовалютой, выпуск токенов
[``` blockchain ```](blockchain) | Реализация блокчейн
[``` smartcontracts ```](smartcontracts) | Смартконтракты
[``` image ```](image) | Обработка изображений
[``` upload ```](upload) | Загрузка файлов на сервер с компьютера
[``` bash ```](bash) | Терминал, BASH команды
[``` git ```](git) | Git команды
[``` algorithm ```](algorithm) | Алгоритмы
[``` competition ```](competition) | Хакатоны, бизнес-кейсы и соревнования
[``` editor ```](editor) | WYSIWYG-редакторы
[``` math ```](math) | Математические вычисления и визуализация
[``` time ```](time) | Работа со временем, датами
[``` microcontroller ```](microcontroller) | Программирование микроконтроллеров
[``` thread ```](thread) | Многопоточность
[``` jwt ```](jwt) | JWT

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
[``` encode ```](encode) | Кодировки

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
sudo git fetch --all
sudo git reset --hard origin/master
sudo git pull origin master
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

## MongoDB
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

```
sudo service mongod start
```

```
brew services start mongodb-community@4.4
```

## Установка модулей в Jupyter Notebook
```
import sys
!{sys.executable} -m pip install pandas
```

## Запуск Back-end
```
env/bin/gunicorn app:app -k eventlet -w 1 -b :5000 --reload
```

## Запуск Front-end
```
serve -s build -p 3000
```

## Запуск Docker Compose
```
docker-compose -f docker-compose.yml up --build
```

## Очистка Docker
```
docker system prune -a
```

## Подключение к Docker контейнеру
```
docker exec -it <> bash
```

## Включение Debug сокетов в консоли браузера
```
localStorage.setItem('debug', 'socket.io-client:socket')
```