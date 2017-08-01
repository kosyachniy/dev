# Разработка
[![Travis CI](https://travis-ci.org/kosyachniy/dev.svg?branch=master)](https://travis-ci.org/kosyachniy/dev/)

Не решено
---
№ | Где | Ошибка | Решение
---|---|---|---
1 | ``` ai/tensorflow ``` | Попробовать обучать нейронные сети после нахождения весов мат алгоритмами | Пройти курс..
2 | ``` compile ``` | Найти способ запуска Python как приложения | Пакетирование / Cython

API
---
&nbsp; | Python | C++ | PHP
---|---|---|---
GUI | [PyQt](http://pyqt.sourceforge.net/Docs/PyQt5/) |  |
ИИ | [TensorFlow](https://www.tensorflow.org/api_docs/python/) |  |
ВКонтакте | [VK](https://vk.com/dev/methods) |  |
Twitter | [TweePy](http://docs.tweepy.org/en/v3.5.0/api.html) |  |
InstaGram |  |  |

Обучение
---
Предмет | Расположение | Уроки | Код
---|---|---|---
Регулярные выражения | ``` regular ``` | [Wikipedia](https://ru.wikipedia.org/wiki/%D0%A0%D0%B5%D0%B3%D1%83%D0%BB%D1%8F%D1%80%D0%BD%D1%8B%D0%B5_%D0%B2%D1%8B%D1%80%D0%B0%D0%B6%D0%B5%D0%BD%D0%B8%D1%8F) |
MNIST | ``` ai/tensorflow/mnist ``` | [Google](https://codelabs.developers.google.com/codelabs/cloud-tensorflow-mnist/#0) | [GitHub](https://github.com/martin-gorner/tensorflow-mnist-tutorial)
GUI | ``` gui ``` | [PythonWorld](https://pythonworld.ru/gui) |
HTML / CSS  | ``` style ``` | [HTMLBook](http://htmlbook.ru/) |
JS | ``` js ``` | [JavaScript](http://learn.javascript.ru/) |
AI | ``` ai/tensorflow ``` | [Stepik](https://stepik.org/course/%D0%9D%D0%B5%D0%B9%D1%80%D0%BE%D0%BD%D0%BD%D1%8B%D0%B5-%D1%81%D0%B5%D1%82%D0%B8-401/syllabus)<br>[HabraHabr 1](https://habrahabr.ru/post/312450/)<br>[HabraHabr 2](https://habrahabr.ru/post/313216/) |

Решение
---
[Онлайн компилятор](http://ideone.com/)

Тип | Сервис
---|---
Олимпиадные задачи | [CodeForces](http://codeforces.com/problemset)
Олимпиады | [Яндекс.Алгоритм](https://academy.yandex.ru/events/algorithm/)<br>[VK Cup](http://codeforces.com/vkcup2017)<br>[Russian Code Cup](http://www.russiancodecup.ru/ru/)<br>[FaceBook Hacker Cup](https://ru.wikipedia.org/wiki/Facebook_Hacker_Cup)<br>[Google Code Jam](https://code.google.com/codejam/)<br>[КРОК](https://www.croc.ru/vacancy/students/detail/61353/)
Конкурсы | [Web Ready](http://www.gotech.vc/)<br>[Список](https://habrahabr.ru/company/ingria_startup/blog/138718/)
Работа | [HeadHunter](https://spb.hh.ru/search/vacancy?text=python&area=2)

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

Языки программирования
---
&nbsp; | [Python](https://github.com/kosyachniy/dev/wiki/Python) | [C++](https://github.com/kosyachniy/dev/wiki/C) | [PHP](https://github.com/kosyachniy/dev/wiki/PHP) | [Pascal](https://github.com/kosyachniy/dev/wiki/Pascal) | [JavaScript](https://github.com/kosyachniy/dev/wiki/JavaScript)
---|---|---|---|---|---
Расширение | .py | .cpp<br>.h | .php | .pas | .js
Арифметические знаки | + - / // % * ** |  |  |  |
Сложная арифметика | += -= /= //= %= *= **= |  |  |  |
Присваивание | = | = | = | := | =
Сравнение | == > < >= <= != | == > < >= <= != | == > < >= <= != | = > < >= <= <> | 
Логика | and; or; not; in; not in |  |  |  | 
Двойное присваивание<br>(a=b=1) | да |  |  |  |
Объединённая логика<br>(4<a<6) | да |  |  |  |
Присваивание внутри выражения<br>(if (x=2)==2) | нет |  |  |  |
Объявление типов данных | нет | да | нет | да |
Указатели / переменные | указатели<br>(изменяемые / неизменяемые типы данных) | переменные |  |  |
Изменяемые переменные | списки |  |  |  |
Неизменяемые переменные | числа<br>строки<br>кортежи |  |  |  | 
Начало индексации | 0 | 0 | 0 |  |
Математика<br>(0.3+0.3+0.3=0.(9)) | да |  |  |  |
Бинарные операции | >> << |  |  |  |
Синтаксис | функция условия:<br>&emsp;функция(параметры) | функция (условия)<br>&emsp;{<br>&emsp;функция(параметры);<br>&emsp;} |  |  |
Разметка | … | #include <iostream><br><br>using namespace std;<br><br>int main()<br>&emsp;{<br>&emsp;…<br>&emsp;return 0;<br>&emsp;} | <?php<br>…<br>?> |  | …
Строка | '...'<br>"..." | '...'<br>"..." | '...'<br>"..." | '...' |
Комментарий | ```#```<br>```''' … '''```<br>```""" … """``` | ```//``` | ```//``` | ```//```<br>```{...}``` | 
Название переменной | ```буквычисла``` | ```буквычисла```<br>!!! ```верблюжийРегистр``` | ```$буквычисла``` |  | 
Типы данных |  |  |  |  |
Особые параметры<br>(_=_) | да |  |  |  |
Конец функции | enter | ```;``` | ```;``` | ```;``` | ```;```
Объединение строк | ```+``` | ```+``` | ```.``` | ```+``` | ```+```
Перевод строки | ```\n``` | ```\n``` | enter |  |
Передача функций как параметр | да | да |  |  |
Присваивание нескольких значений | да | нет |  |  |
Тип исполнения | интерпретируемый | компилируемый | интерпретируемый | компилируемый | интерпретируемый
Запуск | ```python _.py``` | ```g++ _.cpp -o _```<br>```./_``` | веб-страница<br>!!! веб-сервер |  | веб-страница
Умножение строки на число | да |  |  |  |
Подключение библиотек | ```import …```<br>```from … import … as …``` | ```#include <….h>```<br>```#include "….h"``` | ```include('…');``` |  |
Если | if …:<br>&emsp;…<br>elif …:<br>&emsp;…<br>else:<br>&emsp;… | if (…)<br>{<br>…<br>}<br>else<br>{<br>…<br>} | if (…)<br>{<br>…<br>}<br>elseif (…)<br>{<br>…<br>}<br>else<br>{<br>…<br>} |  |
Цикл со счётчиком | for _ in _:<br>&emsp;… | for (…;…;…)<br>&emsp;{<br>&emsp;…<br>&emsp;} | for (…;…;…)<br>&emsp;{<br>&emsp;…<br>&emsp;} |  |
Цикл с условием | while ...:<br>&emsp;... | while (...)<br>&emsp;{<br>&emsp;...<br>&emsp;} | while (...)<br>&emsp;{<br>&emsp;...<br>&emsp;} |  |
Цикл с постусловием | нет | do<br>&emsp;{<br>&emsp;...<br>&emsp;}<br>while (...) |  |  |
Выбор |  |  |  |  |
Функция | def _(…, _=_):<br>&emsp;…<br>&emsp;return … | тип данных _(…)<br>&emsp;{<br>&emsp;…<br>&emsp;return _;<br>&emsp;} | function _(…)<br>&emsp;{<br>&emsp;…<br>&emsp;return _;<br>&emsp;} | function<br>procedure | 
Объект | class _:<br>&emsp;def<br>&emsp;\_\_init\_\_(self,…,_=_):<br>&emsp;&emsp;…<br>&emsp;…<br>&emsp;\_\_exit\_\_(self,…,_=_):<br>&emsp;&emsp;... | class имя<br>&emsp;{<br>&emsp;public:<br>&emsp;имя (…)<br>&emsp;&emsp;{<br>&emsp;&emsp;…<br>&emsp;&emsp;}<br>&emsp;…<br>&emsp;~имя ()<br>&emsp;&emsp;{<br>&emsp;&emsp;…<br>&emsp;&emsp;}<br>&emsp;private:<br>&emsp;…<br>&emsp;protected:<br>&emsp;…<br>&emsp;} |  |  |
Ввод | ```…=input()```<br>!!! Текст, для чисел ```int(…)``` | ```cin >> _ >> _;``` | нет |  |
Вывод | ```print(…, end='…')``` | ```cout << _ << _ << endl;``` | ```print …;```<br>```echo …;``` |  |
Исключения |  |  |  |  |
Особенности | List / Dictionary Comprehension<br>Однострочная функция lambda<br>Трёхместное выражение if/else<br> |  |  |  |
