from flask import session, request, render_template, redirect
from app import app, LINK

from requests import post
import re, json

@app.route('/sys_add_article', methods=['POST'])
def sys_add_article():
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

	req = post(LINK, json=req).text

	if req.isdigit():
		return render_template('message.html', cont=req)

	req = json.loads(req)

	return redirect(LINK + str(req['id']))