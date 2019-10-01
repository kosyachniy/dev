from flask import Flask
from flask_cors import CORS

# from keys import CAPTCHA
# from sets import SERVER, CLIENT


# Логирование

# import logging
# logging.basicConfig(filename='error.log', level=logging.DEBUG)

#

app = Flask(__name__)
app.config.from_object('config')
CORS(app, resources={r'/*': {'origins': '*'}})

# Socket.IO

from flask_socketio import SocketIO

sio = SocketIO(app, async_mode=None)

#


from app import api
from app import sockets