# ZEIT NOW

## [Начало работы](https://zeit.co/github-setup)

## Установка
### CLI
```
brew update
brew cask install now
now login
```

``` ~/.now ```

## Развёртывание
1. Перейти в корень проекта
2. ``` now ```
3. Перейти по полученной ссылке

## Разработка
[Документация](https://zeit.co/docs/), [Примеры](https://github.com/zeit/now-examples)

### Python
[Flask -> Now](https://camillovisini.com/barebone-serverless-flask-rest-api-on-zeit-now/)

```
python3 -m venv flask
source flask/bin/activate
pip3 install flask ...
pip3 freeze > requirements.txt
deactivate

touch now.json index.py
```

``` now.json ```
```
{
	"version": 2,
	"name": "dev",
	"builds": [
		{"src": "*.py", "use": "@liudonghua123/now-flask", "config": {"maxLambdaSize": "30mb"}}
	],
	"routes": [
		{"src": "/.*", "dest": "/"}
	]
}
```

``` index.py ```
```
from flask import Flask
from flask_restplus import Resource, Api, fields
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app,
	version='0.1',
	title='Our sample API',
	description='This is our sample API'
)

@api.route('/hello_world')
class HelloWorld(Resource):
	def get(self):
		return {'hello': 'world'}

if __name__ == '__main__':
	app.run(debug=True)
```

Проверка: ``` python3 index.py ```

``` http://127.0.0.1:5000/hello_world ```

## Управление
[Запущенные](https://zeit.co/dashboard/deployments)