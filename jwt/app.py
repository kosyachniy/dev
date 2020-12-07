# Main app

from flask import Flask
app = Flask(__name__)

# CORS

from flask_cors import CORS
CORS(app, resources={r'/*': {'origins': '*'}})

# API

import json
from functools import wraps

import jwt

with open('keys.json', 'r') as file:
	SECRET_KEY = json.loads(file.read())['jwt']

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		try:
			header = request.headers.get('Authorization')
			token = header.split(' ')[1]

			if not token:
				return jsonify({'message': 'Token is missing!'}), 403

			try:
				data = jwt.decode(token, SECRET_KEY)
				kwargs['data'] = data
			except:
				return jsonify({'message': 'Token is invalid!'}), 403

			return f(*args, **kwargs)

		except Exception as e:
			print('ERR', e)
			return f(*args, **kwargs)

	return decorated

@app.route('/', methods=['POST'])
@token_required
def index(data={}):
	x = request.json
	print(x, data)

	return jsonify(x)