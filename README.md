# Разработка
![Travis CI](https://travis-ci.org/kosyachniy/dev.svg?branch=master)

[Разметка README.md](http://coddism.com/zametki/razmetka_readmemd_v_github)

[Travis CI](https://travis-ci.org/kosyachniy/dev/)
.travis.yml | Язык программирования
---|---
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
install: "pip install -r requirements.txt"
script: pytest | Python


Код | Действие
---|---
``` pip freeze > requirements.txt ``` | Получить requerements.txt
