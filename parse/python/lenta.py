import time
import json

import requests
from bs4 import BeautifulSoup


URL = 'https://lenta.ru/rubrics/{}/'
categories = ('russia', 'world', 'ussr', 'economics', 'forces', 'science', 'culture', 'sport', 'media', 'style', 'travel', 'life', 'realty')

for category in categories:
	print('-'*100)
	print(category)
	print('-'*100)

	with open('data/lenta/{}.json'.format(category), 'a') as file:
		# Получаем html-код

		html = requests.get(URL.format(category)).text

		# Парсинг

		soup = BeautifulSoup(html, 'html.parser') # lxml

		section1 = soup.select('div.js-rubric__content')[0]
		section2 = section1.find('div', {'class': 'js-content'})
		divs = section2.findAll('div', {'class': 'item'})

		for div in divs:
			try:
				a = div.h3.a
			except:
				continue

			url = 'https://lenta.ru' + a.attrs['href']
			name = a.text.strip()

			row = url + ' ' + name
			if len(row) > 125:
				row = row[:122] + '...'
			print('{:125}'.format(row), end='	')

			# Получаем html-код

			html2 = requests.get(url.format(category)).text

			# Парсинг

			soup2 = BeautifulSoup(html2, 'html.parser')

			# title = soup2.h1.text
			# subtitle = soup2.h2.text

			body = soup2.find('div', {'itemprop': 'articleBody'})

			if not body:
				body = soup2.find('article', {'class': 'b-topic'})

			if not body:
				print('❌')
				continue

			cont = body.text

			print('✔', len(cont.split()))


			req = {
				'url': url,
				'name': name,
				'cont': cont,
			}
			data = json.dumps(req, ensure_ascii=False)

			print(data, file=file)

			time.sleep(1)