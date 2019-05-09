from flask import session, request, render_template, redirect
from app import app, LINK

from requests import post
import re, json, base64

@app.route('/sys_question_add', methods=['POST'])
def sys_question_add():
	x = request.form

	req = {
		'method': 'question.add',
		'name': x['name'],
		'category': int(x['category']),
	}

	if 'cont' in x: req['cont'] = x['cont']
	if 'tags' in x: req['tags'] = [i.strip() for i in re.compile(r'[a-zA-Zа-яА-Я ]+').findall(x['tags'])]

	if 'images' in request.files:
		y = request.files['images'].stream.read()
		y = str(base64.b64encode(y))[2:-1]
		req['images'] = y
		req['file'] = request.files['images'].filename

	req = post(LINK, json=req).text

	if req.isdigit():
		return render_template('message.html', cont=req)

	req = json.loads(req)

	return redirect(LINK + 'question/' + str(req['id']))