from flask import session, request, render_template
from app import app, LINK, get_url

from requests import post

@app.route('/settings', methods=['POST'])
def settings():
	x = request.form

	if 'token' not in session:
		return render_template('message.html', cont='3')

	req = {'cm': 'profile.settings', 'token': session['token']}
	for i in ('name', 'surname', 'description'): #mail #password
		if i in x: req[i] = x[i]

	req = post(LINK, json=req).text

	if req != '0' and len(req) < 3:
		return render_template('message.html', cont=req)

	return get_url(request.args.get('url'))