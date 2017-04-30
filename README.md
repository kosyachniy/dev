# Разработка
![Travis CI](https://travis-ci.org/kosyachniy/dev.svg?branch=master)

MarkDown
---
[Разметка README.md](http://coddism.com/zametki/razmetka_readmemd_v_github)

Код | Действие
---|---
``` <br> ``` | Энтер


Travis CI
---
[Travis CI](https://travis-ci.org/kosyachniy/dev/)

.travis.yml | Язык программирования
---|---
``` install: "pip install -r requirements.txt" ``` | Python

```
language: 
script: 
```


Терминал
---
Код | Действие
---|---
``` pip freeze > requirements.txt ``` | Получить requerements.txt


Режимы файлов
---
Режим | Обозначение
---|---
r | Открытие на чтение (является значением по умолчанию).
w | Открытие на запись, содержимое файла удаляется, если файла не существует, создается новый.
x | Открытие на запись, если файла не существует, иначе исключение.
a | Открытие на дозапись, информация добавляется в конец файла.
b | Открытие в двоичном режиме.
t | Открытие в текстовом режиме (является значением по умолчанию).
\+ | Открытие на чтение и запись
