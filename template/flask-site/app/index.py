from flask import render_template, session
from app import app, LINK

from requests import post
from json import loads

@app.route('/', methods=['GET'])
@app.route('/index')
def index():
	competions = loads(post(LINK, json={'cm': 'competions.gets', 'num': 2}).text)
	users = loads(post(LINK, json={'cm': 'participants.gets', 'num': 5}).text)

	return render_template('index.html',
		title = 'Главная',
		description = '',
		url = 'index',
		competions = competions,
		users = users,
		user = {'login': session['login'] if 'token' in session else None},
	)