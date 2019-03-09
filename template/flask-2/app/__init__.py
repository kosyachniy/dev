import json
import requests

from flask import Flask
app = Flask(__name__)

@app.route("/", methods=["GET"])
def get():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/post", methods=["GET"])
def post():
    res = requests.post('http://157.230.103.16:5000/sys').text
    return res

@app.route("/sys", methods=["POST"])
def sys():
    return json.dumps({'123': 456, '789': 'str'})