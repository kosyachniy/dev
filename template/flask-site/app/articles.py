from flask import render_template, session
from app import app, LINK, get_preview

from requests import post
from json import loads

@app.route('/<cat>')
@app.route('/<cat>/<sub>')
def articles(cat, sub=''):
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	tags = ['Статьи',]
	category = 0
	subcategory = 0
	title = 'Статьи'
	for x in categories:
		if x['url'] == cat:
			title = x['name'] # Если подкатегория была удалена - останется основная
			tags.append(x['name'])
			category = x['id']

			if sub:
				for i in categories:
					if i['parent'] == x['id'] and i['url'] == sub:
						title = i['name']
						tags.append(i['name'])
						subcategory = i['id']

			break

	articles = loads(post(LINK, json={'method': 'articles.gets', 'category': subcategory if subcategory else category}).text)

	return render_template('articles.html',
		title = title,
		description = '',
		tags = tags,
		url = cat + '/' + sub,
		categories = categories,
		user = user,
		category = category,
		subcategory = subcategory,
		preview = get_preview,

		articles = articles,
	)