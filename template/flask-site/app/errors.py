from flask import render_template
from app import app

@app.errorhandler(404)
def not_found_error(error):
	return render_template('message.html', cont='Страница не существует'), 404