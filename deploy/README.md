# Развёртывание
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