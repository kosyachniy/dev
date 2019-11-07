from flask import render_template, session
from app import app, LINK

from requests import post
from json import loads

@app.route('/admin')
def admin():
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	return render_template('admin.html',
		title = 'Панель администратора',
		description = '',
		tags = ['Панель администратора', 'Админка'],
		url = 'admin',
		categories = categories,
		user = user,
		category = -1,
	)