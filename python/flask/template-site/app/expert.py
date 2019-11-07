from flask import render_template, session, request, Markup
from app import app, LINK, get_preview

from requests import post
from json import loads
import markdown

@app.route('/user/<int:id>')
def expert(id):
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	category = 0
	subcategory = 0
	for i in categories:
		if i['id'] == article['category']:
			if i['parent']:
				category = i['parent']
				subcategory = i['id']
			else:
				category = i['id']
			break

	return render_template('user.html',
		title = article['name'],
		description = article['description'],
		tags = article['tags'],
		url = article['id'],
		categories = categories,
		user = user,
		category = category,
		subcategory = subcategory,
		preview = get_preview,
	)