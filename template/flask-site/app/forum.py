from flask import render_template, session
from app import app, LINK, get_preview

from requests import post
from json import loads

@app.route('/forum')
def forum():
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	questions = []
	for i, category in enumerate(categories):
		if not category['parent'] and category['plus'] == 'article':
			questions.append({
				'url': category['url'],
				'name': category['name'],
				'questions': loads(post(LINK, json={
					'method': 'questions.gets',
					'category': category['id']
				}).text)
			})

	return render_template('forum.html',
		title = 'Форум',
		description = '',
		tags = [],
		url = 'experts',
		categories = categories,
		user = user,
		preview = get_preview,

		questions = questions,
	)