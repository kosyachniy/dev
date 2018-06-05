from flask import Flask, redirect

app = Flask(__name__)
app.config.from_object('config')

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
from app import articles