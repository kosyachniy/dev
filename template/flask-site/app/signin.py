from flask import session, request, render_template
from app import app, LINK, get_url

from requests import post

@app.route('/signin', methods=['POST'])
def signin():
	x = request.form

	if not all([i in x for i in ('login', 'pass')]):
		return render_template('message.html', cont='3')

	req = post(LINK, json={'cm': 'profile.auth', 'login': x['login'], 'pass': x['pass']}).text

	if len(req) < 3:
		return render_template('message.html', cont=req)

	session['token'] = req
	session['login'] = x['login']

	return get_url(request.args.get('url'))