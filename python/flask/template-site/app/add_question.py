from flask import render_template, session, request
from app import app, LINK

from requests import post
from json import loads

@app.route('/admin/add/question')
@app.route('/admin/add/question/')
def add_question():
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	id = request.args.get('i')
	id = int(id) if id else 0

	return render_template('add_question.html',
		title = 'Добавить вопрос',
		description = '',
		tags = ['Панель администратора', 'Админка', 'Добавить вопрос'],
		url = 'admin/add/question?i=%d' % id,
		categories = categories,
		user = user,
		category = -1,

		selected = id,
	)