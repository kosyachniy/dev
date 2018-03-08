import requests, time, json
from bs4 import BeautifulSoup

url='http://mfd.ru/news/company/view/?id=3&page='

with open('db.txt', 'w') as file:
	for s in range(893):
		query=str(s)
		page = requests.get(url + query).text
		soup = BeautifulSoup(page, 'lxml')
		table = soup.find('table', id='issuerNewsList')
		tr=table.find_all('tr')
		for i in tr:
			td=i.find_all('td')
			date=td[0].contents[0].strip()
			name=td[1].a.contents[0].strip()
			print(date, name)
			a=json.dumps({'date':date, 'name':name}, ensure_ascii=False)
			print(a, file=file)
		time.sleep(1)