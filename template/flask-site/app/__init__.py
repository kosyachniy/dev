from flask import Flask, redirect, request

import gzip
import io
import json
from flask.views import MethodView

def gzip_http_request_middleware():
    encoding = request.headers.get('content-encoding', '')
    if encoding == 'gzip':
        gz = request.get_data()
        zb = io.BytesIO(gz)
        zf = gzip.GzipFile(fileobj=zb)
        clear = zf.read()
        request._cached_data = clear

class JsonEchoViewClass(MethodView):
    def post(self):
        data = request.get_json()
        out = 'Request Payload:\n'
        if data:
            out += json.dumps(data, indent=2)
        else:
            out += ' * No data received.'
        out += '\n'
        return out


def json_echo_view_function():
    data = request.get_json()
    out = 'Request Payload:\n'
    if data:
        out += json.dumps(data, indent=2)
    else:
        out += ' * No data received.'
    out += '\n'
    return out


app = Flask(__name__)
app.config.from_object('config')

app.before_request(gzip_http_request_middleware)
app.add_url_rule('/', 'echo', json_echo_view_function, methods=['POST', ])
app.add_url_rule('/alt/', view_func=JsonEchoViewClass.as_view('alt'))


LINK = 'http://167.99.128.56/'

def get_url(url, rep='competions'):
	if not url: url = rep
	if url == 'index': url = ''
	return redirect(LINK + url)

from app import process

from app import index

from app import login
from app import signup
from app import signin
from app import out

from app import errors

from app import cabinet
from app import settings
from app import edit
from app import avatar
from app import image

from app import admin
from app import add

from app import sys_add_article

from app import article
from app import articles