from flask import render_template, session
from app import app, LINK

from requests import post
from json import loads

@app.route('/participants/<user>')
def participant(user):
	x = loads(post(LINK, json={'cm': 'participants.get', 'login': user}).text)

	return render_template('participant.html',
		title = x['surname'] + ' ' + x['name'],
		description = 'Хочу попасть в команду, ищу конкурс или стартап',
		url = 'participants/' + user,
		participant = x,
		user = {'login': session['login'] if 'token' in session else None},
	)