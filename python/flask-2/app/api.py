from flask import request, jsonify
from app import app


@app.route('/')
def get():
	name = request.args.get('name')

	return '<html><body><h1>Hello, {}!</h1></body></html>'.format(name)

@app.route('/', methods=['POST'])
def post():
	x = request.json

	return jsonify(x)