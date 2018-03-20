from flask import render_template, request, jsonify
from app import app

@app.route('/', methods=['POST'])
def hello():
	x = request.json
	print(x)
	return jsonify(x)