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