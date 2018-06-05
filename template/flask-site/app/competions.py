from flask import render_template, session
from app import app, LINK

from requests import post
from json import loads

@app.route('/competions')
def competions():
	x = loads(post(LINK, json={'cm': 'competions.gets'}).text)

	return render_template('competions.html',
		title = 'Соревнования',
		description = 'Соревнования, хакатоны, стартапы, конкурсы, олимпиады, конференции, проекты',
		url = 'competions',
		competions = x,
		user = {'login': session['login'] if 'token' in session else None},
		organizer = ('Яндекс', 'Mail.Ru', 'CSC', 'Epam', 'Changellenge', 'Google', 'Microsoft', 'Intel'),
		specialization = ('IT', 'Бизнес-задачи', 'Смешанные'),
		type = ('Хакатон', 'Стажировка', 'Конференция', 'Стартап', 'Олимпиада'),
		city = ('Санкт-Петербург', 'Москва'),
		stage = ('Отборочный', 'Полуфинал', 'Финал'),
	)