from flask import render_template, session
from app import app, LINK

from requests import post
from json import loads

@app.route('/<category>')
@app.route('/<category>/<sub>')
def articles(category, sub=''):
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	articles = loads(post(LINK, json={'method': 'articles.gets', 'count': 6}).text)

	t = True
	for x in categories:
		if t and x['url'] == category:
			if sub:
				for i in categories:
					if i['parent'] == x['id'] and i['url'] == sub:
						title = i['name']
						t = False
			else:
				title = x['name']
				t = False

	return render_template('articles.html',
		title = title,
		description = '',
		url = category,
		categories = categories,
		user = user,

		articles = articles,
	)