# Python
## Обучение
### Курсы
* МФТИ & Mail.Ru: [Coursera](https://www.coursera.org/learn/programming-in-python/home/welcome)
* [YouTube](https://www.youtube.com/watch?list=PL1A2CSdiySGIPxpSlgzsZiWDavYTAx61d&time_continue=3&v=CkIrizsP64c)
* [PythonWorld](https://pythonworld.ru/samouchitel-python)

### Справочники
* [Туториалы, примеры](https://pythonworld.ru/)
* [Code style: PEP8](https://pythonworld.ru/osnovy/pep-8-rukovodstvo-po-napisaniyu-koda-na-python.html)
* [Стандартные библиотеки](https://docs.python.org/3/library/)

## Справка
### Получение запросов
Команда | Значение
---|---
``` request.json['name'] ``` | POST параметры
``` request.args.get('name') ``` | GET параметры
``` request.values.get('name') ``` | Пара ключ/значение в виде параметра POST-запроса
``` request.get_data() ``` | 

## Список команд
### Терминал
Код | Действие
---|---
``` pip freeze > requirements.txt ``` | Получить requerements.txt
``` jupyter notebook ``` | Запустить блокнот