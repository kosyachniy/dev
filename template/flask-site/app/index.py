from flask import render_template, session
from app import app, LINK

from requests import post
from json import loads

@app.route('/', methods=['GET'])
@app.route('/index')
def index():
	articles = loads(post(LINK, json={'method': 'articles.gets', 'count': 6}).text)

	return render_template('index.html',
		title = 'Главная',
		description = '',
		url = 'index',
		categories = loads(post(LINK, json={'method': 'categories.gets'}).text),
		user = {'login': session['login'] if 'token' in session else None},

		articles = articles,
	)