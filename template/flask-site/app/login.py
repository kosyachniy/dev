from flask import render_template, session, request
from app import app

from requests import post
from json import loads

@app.route('/login')
def login():
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	return render_template('login.html',
		title = 'Логин', #Аккаунт
		description = 'Регистрация / Авторизация',
		url = request.args.get('url'),
		user = user,
	)