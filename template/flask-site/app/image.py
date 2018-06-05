from flask import session, request, render_template, redirect
from app import app, LINK

from requests import post
import base64, json

@app.route('/image', methods=['POST'])
def image():
	x = request.files['file'].stream.read()
	x = str(base64.b64encode(x))[2:-1]

	id = request.args.get('id')

	if not id or 'token' not in session:
		return render_template('message.html', cont='3')

	images = json.loads(post(LINK, json={'cm': 'competions.get', 'id': int(id), 'token': session['token']}).text)
	images = images['images'] if 'images' in images else []
	images.append(x)

	req = post(LINK, json={'cm': 'competions.edit', 'id': int(id), 'token': session['token'], 'images': images}).text

	if req != '0' and len(req) < 3:
		return render_template('message.html', cont=req)

	return redirect(LINK + 'competions/' + id)