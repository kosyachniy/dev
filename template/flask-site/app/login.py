from flask import render_template, session, request
from app import app, LINK

from requests import post
from json import loads

@app.route('/login')
def login():
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	redirect = request.args.get('url')

	return render_template('login.html',
		title = 'Логин', #Аккаунт
		description = 'Регистрация / Авторизация',
		url = 'login?url=' + redirect,
		user = user,
		categories = categories,
		without_menu = True,

		redirect = redirect,
	)