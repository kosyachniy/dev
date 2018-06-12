from flask import session, request, render_template, redirect
from app import app, LINK

from requests import post
import re, json, base64

@app.route('/sys_article_edit', methods=['POST'])
def sys_article_edit():
	x = request.form

	id = request.args.get('i')

	req = {
		'method': 'articles.edit',
		'id': int(id),
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

	if req.isdigit() and int(req) > 0:
		return render_template('message.html', cont=req)

	return redirect(LINK + str(id))