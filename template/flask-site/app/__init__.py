from flask import Flask, redirect, after_this_request, request
#from flask_compress import Compress
#from cStringIO import StringIO as IO
from io import BytesIO as IO
import gzip
import functools

def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if (response.status_code < 200 or
                response.status_code >= 300 or
                'Content-Encoding' in response.headers):
                return response
            gzip_buffer = IO()
            gzip_file = gzip.GzipFile(mode='wb', fileobj=gzip_buffer)
            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func

app = Flask(__name__)
app.config.from_object('config')
#Compress(app)

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