from flask import session, request, render_template, redirect
from app import app, LINK

from requests import post
import re, json, base64

@app.route('/sys_article_add', methods=['POST'])
def sys_article_add():
	x = request.form

	req = {
		'method': 'articles.add',
		'name': x['name'],
		'category': int(x['category']),
		'cont': x['cont'],
		'tags': [i.strip() for i in re.compile(r'[a-zA-Zа-яА-Я ]+').findall(x['tags'])],
		'description': x['description'],
		'priority': x['priority'] if 'priority' in x else 50,
	}

	if 'preview' in request.files:
		y = request.files['preview'].stream.read()
		y = str(base64.b64encode(y))[2:-1]
		req['preview'] = y

	req = post(LINK, json=req).text

	if req.isdigit():
		return render_template('message.html', cont=req)

	req = json.loads(req)

	return redirect(LINK + str(req['id']))