from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object('config')
CORS(app, resources={r'/*': {'origins': '*'}})


from app import api