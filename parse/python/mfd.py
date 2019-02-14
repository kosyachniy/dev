import time
import json

import requests
from bs4 import BeautifulSoup


# Преобразование строки в timestamp

def parse_time(cont):
	day = cont.split(',')[0]

	if day == 'сегодня':
		cont = time.strftime('%d.%m.%Y', time.localtime()) + cont[cont.find(','):]
	elif day == 'вчера':
		cont = time.strftime('%d.%m.%Y', time.localtime(time.time() - 24*60*60)) + cont[cont.find(','):]

	return time.mktime(time.strptime(cont, '%d.%m.%Y, %H:%M'))


url = 'http://mfd.ru/news/company/view/?id=3&page={}'

with open('data.json', 'w') as file:
	for page in range(958):
		# Получаем html-код

		html = requests.get(url.format(page)).text

		# Парсинг

		soup = BeautifulSoup(html)
		table = soup.find('table', id='issuerNewsList')
		tr = table.find_all('tr')

		for i in tr:
			td = i.find_all('td')

			try:
				date = td[0].contents[0].strip()
				name = td[1].a.contents[0].strip()
			except:
				continue

			req = {
				'name': name,
				'time': parse_time(date),
			}
			data = json.dumps(req, ensure_ascii=False)

			print(data)
			print(data, file=file)

		time.sleep(1)