from flask import render_template, session
from app import app, LINK

from requests import post
from json import loads

@app.route('/participants')
def participants():
	x = loads(post(LINK, json={'cm': 'participants.gets'}).text)

	return render_template('participants.html',
		title = 'Участники',
		description = 'Участники, набор команды, поиск людей в команду',
		url = 'participants',
		users = x,
		user = {'login': session['login'] if 'token' in session else None},
		specialization = ('IT', 'Менеджмент', 'Искусство', 'Экономика', 'Химия', 'Физика', 'Математика', 'История'),
		city = ('Санкт-Петербург', 'Москва'),
		experience = ('Участие в конкурсах', 'Призовые места', 'Первые места', 'Имеет работу'),
		type = ('Хакатон', 'Стажировка', 'Конференция', 'Стартап', 'Олимпиада'),
		rating = ('Раздел в разработке',),
	)