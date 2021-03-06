from flask import render_template, session
from app import app, LINK, get_preview

from requests import post
from json import loads

@app.route('/experts')
def experts():
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	articles = []
	for i, article in enumerate(categories):
		if not article['parent']:
			articles.append({
				'url': article['url'],
				'name': article['name'],
				'articles': loads(post(LINK, json={
					'method': 'articles.gets',
					'category': article['id']
				}).text)
			})

	return render_template('experts.html',
		title = 'Эксперты',
		description = '',
		tags = [],
		url = 'experts',
		categories = categories,
		user = user,
		preview = get_preview,

		articles = articles,
	)