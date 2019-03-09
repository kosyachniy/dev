from flask import request
from app import app

'''
@app.route('/process/<name>')
def index(name):
	print(name)
	return 'Hiii'
'''

@app.route('/')
def login():
	method = request.args.get('cm')
	if method == 'auth':
		username = request.args.get('login')
		password = request.args.get('pass')

		print(username, password)

		return '<html><body><h1>Authorization!</h1>Hi, %s.' % username