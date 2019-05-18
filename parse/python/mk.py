import time
import json

import requests
from bs4 import BeautifulSoup


URL = 'https://www.mk.ru/{}/{}/'
categories = ('politics', 'economics', 'incident', 'social', 'sport', 'culture', 'science')

for category in categories:
	print('-'*100)
	print(category)
	print('-'*100)

	with open('data/mk/{}.json'.format(category), 'w') as file:
		for page in range(1, 5):
			# Получаем html-код

			html = requests.get(URL.format(category, page)).text

			# Парсинг

			soup = BeautifulSoup(html, 'html.parser') # lxml

			ul = soup.select('ul.big_listing')[0]

			for li in ul:
				try:
					a = li.select('a.mkh2')[0]
				except:
					continue

				url = a.attrs['href']
				name = a.text.strip()

				print(url, name, end='	')

				# Получаем html-код

				html2 = requests.get(url.format(category)).text

				# Парсинг

				soup2 = BeautifulSoup(html2, 'html.parser')

				body = soup2.select('div.content')

				if not body:
					 print('❌')
					 continue

				body = body[0]

				# title = body.select('h1')[0]
				# subtitle = body.select('p.second_title')[0]

				cont = body.text

				print('✔', len(cont.split()))


				req = {
					 'url': url,
					 'name': name,
					 'cont': cont,
				}
				data = json.dumps(req, ensure_ascii=False)

				print(data, file=file)

			time.sleep(5)