from flask import render_template, session, request, redirect
from app import app, LINK

from requests import post
from json import loads

@app.route('/cabinet')
def cabinet():
	categories = loads(post(LINK, json={'method': 'categories.gets'}).text)
	user = loads(post(LINK, json={'method': 'users.get', 'id': session['id']}).text) if 'id' in session else {'id': 0, 'admin': 2}

	x = request.args.get('url')

	if 'token' in session:
		return render_template('cabinet.html',
			title = 'Личный кабинет',
			description = 'Личный кабинет, настройки, аккаунт, профиль',
			url = x if x else 'cabinet',
			categories = categories,
			user = user,
		)

	else:
		return redirect(LINK + 'login?url=cabinet')