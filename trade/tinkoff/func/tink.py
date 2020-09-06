import time
import json
import requests
from multiprocessing import Process

from openapi_client import openapi

from func.mongodb import db


with open('keys.json', 'r') as file:
	# token = json.loads(file.read())['tinkoff']['sandbox_token']
	token = json.loads(file.read())['tinkoff']['token']


client = openapi.api_client(token)


# Dollar to ruble exchange rate

def usd_rub(count=1): # TODO: Тинькофф конвертация
	data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()['Valute']['USD']['Value']
	return round(count * data)

# Get FIGI by ticker

def get_figi(ticker):
	# Get quote

	ticker = ticker.upper()
	quote = db['quotes'].find_one({'ticker': ticker}, {'_id': False, 'figi': True})

	# Response

	if quote:
		return quote['figi']

	# API request

	res_ticker = client.market.market_search_by_ticker_get(ticker).payload.instruments

	if len(res_ticker) != 1:
		raise Exception('not found')

	figi = res_ticker[0].figi

	# Get price

	prices = client.market.market_orderbook_get(figi, 2).payload

	# Update DB

	if len(prices.asks) and len(prices.bids):
		quote = {
			'ticker': ticker,
			'figi': figi,
			'buy': prices.asks[0].price,
			'sell': prices.bids[0].price,
		}

	else:
		quote = {
			'ticker': ticker,
			'figi': figi,
			'last': prices.last_price,
		}

	db['quotes'].insert_one(quote)

	# Response

	return figi

# Get price by ticker
# TODO: min lots, min price_increment

def get_price(ticker, signal=1, last=True):
	ticker = ticker.upper()

	if last:
		quote = db['quotes'].find_one({'ticker': ticker})

		# Add new

		if not quote:
			figi = get_figi(ticker)
			quote = db['quotes'].find_one({'ticker': ticker})

		# Get old

		if 'buy' in quote and 'sell' in quote:
			return (quote['buy'], quote['sell'])[signal]
		else:
			return quote['last']

	# Realtime

	figi = get_figi(ticker)
	prices = client.market.market_orderbook_get(figi, 2).payload

	if len(prices.asks) and len(prices.bids):
		if signal == -1:
			return prices.asks[0].price, prices.bids[0].price
		else:
			return (prices.asks[0].price, prices.bids[0].price)[signal]
	else:
		raise Error('closed')

# Get portfolio

def portfolio_get():
	## Currencies

	portfolio = client.portfolio.portfolio_currencies_get().payload.currencies
	currencies = []

	for i in portfolio:
		if i.balance > 0:
			currencies.append({
				'name': ('$', '€', '₽')[('USD', 'EUR', 'RUB').index(i.currency)],
				'cont': i.balance,
				'usd': i.balance / usd_rub() if i.currency == 'RUB' else i.balance, # TODO: EUR
			})

	currencies.sort(key=lambda i: i['usd'], reverse=True)

	## Stocks

	portfolio = client.portfolio.portfolio_get().payload.positions
	stocks = []

	for i in portfolio:
		if i.instrument_type == 'Stock':
			price = get_price(i.ticker) # TODO: данные из метода

			req = {
				'name': i.ticker,
				'cont': int(i.balance),
				'price': price,
				'currency': i.average_position_price.currency,
			}

			req['usd'] = req['cont'] * price
			if req['currency'] == 'RUB': # TODO: EUR
				req['usd'] /= usd_rub()

			stocks.append(req)

	stocks.sort(key=lambda i: i['usd'], reverse=True)

	return stocks, currencies

# Get order

def orders_get(): # TODO: стилизация
	return client.orders.orders_get().payload

# Cancel order

def orders_cancel(order_id): # TODO: стилизация
	return client.orders.orders_cancel_post(order_id).payload

# Buy share
# TODO: min lots, min price_increment

def shares_buy(ticker, count, price): # TODO: переименовать название методов
	figi = get_figi(ticker)

	res = client.orders.orders_limit_order_post(figi, {
		'price': price,
		'lots': count,
		'operation': 'Buy',
	}).payload

	return res.order_id

# Sell share
# TODO: min lots, min price_increment

def shares_sell(ticker, count, price):
	figi = get_figi(ticker)

	res = client.orders.orders_limit_order_post(figi, {
		'price': price,
		'lots': count,
		'operation': 'Sell',
	}).payload

	return res.order_id


def update_price():
	while True:
		# Биржа закрыта

		time_cur = time.gmtime()
		wday = time_cur.tm_wday
		hour = time_cur.tm_hour
		munit = time_cur.tm_min

		if wday in (5, 6) or hour < 7 or hour >= 23 or (hour >= 22 and minuts > 40):
			time.sleep(300)
			continue

		# Регулярные задачи

		for quote in db['quotes'].find():
			prices = client.market.market_orderbook_get(quote['figi'], 2).payload

			if len(prices.asks) and len(prices.bids):
				quote['buy'] = prices.asks[0].price
				quote['sell'] = prices.bids[0].price

				if 'last' in quote:
					del quote['last']

			else:
				quote['last'] = prices.last_price

				if 'buy'in quote and 'sell' in quote:
					del quote['buy']
					del quote['sell']

			db['quotes'].save(quote)

			time.sleep(1) # 120 запросов в секунду

p = Process(target=update_price)
p.start()