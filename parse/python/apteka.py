import time
import json

import requests
from bs4 import BeautifulSoup


LINK = 'https://apteka.ru'
url = LINK + '/category/vitamin-mineral/vitamins/?PAGEN_1={}'

with open('data.json', 'w') as file:
	for page in range(1, 45):
		# Получаем html-код

		html = requests.get(url.format(page)).text

		# Парсинг

		soup = BeautifulSoup(html, 'html.parser')

		table = soup.find('div', {'class': 'catalog-list'})
		articles = soup.find_all('article', {'class': 'item'})

		for article in articles:
			try:
				name = article.find('div', {'class': 'item_title-info'}).text
				src = article.find('figure', {'class': 'item_img'}).a.get('href')
				img = article.find('img').get('src')
				price = article.find('div', {'class': 'price'}).span.text
			except:
				continue

			req = {
				'name': name.strip(),
				'link': LINK + src,
				'img': LINK + img,
				'price': float(price),
			}
			data = json.dumps(req, ensure_ascii=False, indent='\t')

			print(data)
			# print(data, file=file)

		time.sleep(1)