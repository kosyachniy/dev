from flask import Flask, request, jsonify


app = Flask(__name__)


@app.route('/')
def get():
	name = request.args.get('name')

	return '<html><body><h1>Hello, {}!</h1></body></html>'.format(name)

@app.route('/', methods=['POST'])
def post():
	x = request.json

	return jsonify(x)


app.run(host='0.0.0.0')