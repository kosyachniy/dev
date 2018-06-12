from flask import render_template, session, request, Markup
from app import app, LINK, get_preview

from requests import post
from json import loads
import markdown

@app.route('/<int:id>')
def article(id):
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	article = loads(post(LINK, json={'method': 'articles.get', 'id': id}).text)
	article2 = dict(article)
	article2['cont'] = Markup(markdown.markdown(article2['cont']))

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

	edit = request.args.get('edit')

	return render_template('edit.html' if edit else 'article.html',
		title = article['name'],
		description = article['description'],
		tags = article['tags'],
		url = article['id'],
		categories = categories,
		user = user,
		category = category,
		subcategory = subcategory,
		preview = get_preview,

		article = article if edit else article2,
	)