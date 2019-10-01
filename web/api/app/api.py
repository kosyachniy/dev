from flask import request, jsonify
from app import app


@app.route('/')
def get():
	name = request.args.get('name')

	return '<html><body><h1>Hello, {}!</h1></body></html>'.format(name)

@app.route('/data', methods=['POST'])
@app.route('/data/', methods=['POST'])
def post():
	x = request.json
	print(x)

	return jsonify(x)