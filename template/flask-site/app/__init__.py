from flask import Flask, redirect
import os, re

app = Flask(__name__)
#app.config.from_object('config')

LINK = 'http://167.99.128.56/'

def get_url(url, rep='competions'):
	if not url: url = rep
	if url == 'index': url = ''
	return redirect(LINK + url)

def get_preview(url, num=0):
	url = '/static/load/' + url + '/'
	for i in os.listdir('app' + url):
		if str(num) + '.' in i:
			return url + i
	return url + '0.png'

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