from flask import render_template, session
from app import app, LINK

from requests import post
from json import loads

@app.route('/<category>')
def articles(category):
	articles = loads(post(LINK, json={'method': 'articles.gets', 'count': 6}).text)
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)

	for x in categories:
		if x['url'] == category:
			title = x['name']
			break

	return render_template('index.html',
		title = title,
		description = '',
		url = category,
		categories = categories,
		user = {'login': session['login'] if 'token' in session else None},

		articles = articles,
	)