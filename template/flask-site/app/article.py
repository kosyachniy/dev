from flask import render_template, session
from app import app, LINK

from requests import post
from json import loads

@app.route('/<int:id>')
def article(id):
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	article = loads(post(LINK, json={'method': 'articles.get', 'id': id}).text)

	return render_template('article.html',
		title = article['name'],
		description = article['description'],
		url = article['id'],
		categories = categories,
		user = user,

		article = article,
	)