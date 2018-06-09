from flask import session, request, render_template, redirect
from app import app, LINK

from requests import post

@app.route('/sys_add_article', methods=['POST'])
def sys_add_article():
	x = request.form

	id = request.args.get('id')

	if 'token' not in session or not id:
		return render_template('message.html', cont='3')

	req = {'cm': 'competions.edit', 'id': int(id), 'token': session['token']}
	for i in ('name', 'description', 'cont', 'time', 'durability', 'author', 'quantity', 'type', 'prize', 'url', 'geo', 'stage'): #, 'owners'
		if i in x: req[i] = x[i]

	req = post(LINK, json=req).text

	if req != '0' and len(req) < 3:
		return render_template('message.html', cont=req)

	return redirect(LINK + 'competions/' + id)