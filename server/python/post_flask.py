from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    return jsonify({'error': 0})

if __name__=='__main__':
	app.run()