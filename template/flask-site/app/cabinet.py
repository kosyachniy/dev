from flask import render_template, session, request, redirect
from app import app, LINK

from requests import post
from json import loads

@app.route('/cabinet')
def cabinet():
	x = request.args.get('url')

	if 'token' in session:
		return render_template('cabinet.html',
			title = 'Личный кабинет',
			description = 'Личный кабинет, настройки, аккаунт, профиль',
			url = x if x else 'cabinet',
			user = {'login': session['login']},
			profile = loads(post(LINK, json={'cm': 'participants.get', 'token': session['token']}).text),
		)

	else:
		return redirect(LINK + 'login?url=cabinet')