from flask import session #redirect, request
from app import app

from requests import post

LINK = 'http://167.99.128.56/'

@app.route('/out')
def out():
	if 'token' in session:
		post(LINK, json={'cm': 'profile.exit', 'token': session['token']})
		session.pop('token', None)
		session.pop('login', None)

	return '<script>document.location.href = document.referrer</script>' #redirect(request.url, code=302)