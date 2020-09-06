import time
import json
import requests

from openapi_client import openapi


with open('keys.json', 'r') as file:
	# token = json.loads(file.read())['tinkoff']['sandbox_token']
	token = json.loads(file.read())['tinkoff']['token']

with open('sets.json', 'r') as file:
	TIME_OFFSET = json.loads(file.read())['timezone']


client = openapi.api_client(token)


# Dollar to ruble exchange rate

def usd_rub(count=1): # TODO: Тинькофф конвертация
	data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()['Valute']['USD']['Value']
	return round(count * data)

# Get FIGI by ticker

def get_figi_by_ticker(name):
	ticker = client.market.market_search_by_ticker_get(name).payload.instruments

	if len(ticker) != 1:
		raise Exception('not found')

	return ticker[0].figi

# Get price by ticker

def get_price_by_ticker(name, signal=1, last=True):
	ticker = client.market.market_search_by_ticker_get(name).payload.instruments

	if len(ticker) != 1:
		raise Exception('not found')

	figi = ticker[0].figi
	prices = client.market.market_orderbook_get(figi, 2).payload # TODO: min lots, min price_increment

	if len(prices.asks) and len(prices.bids):
		if signal == -1:
			return prices.asks[0].price, prices.bids[0].price
		else:
			return (prices.asks[0].price, prices.bids[0].price)[signal]
	elif last:
		return prices.last_price
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
			price = get_price_by_ticker(i.ticker) # TODO: данные из метода

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

def shares_buy(ticker, count, price=None): # TODO: стилизация
	figi = get_figi_by_ticker(ticker)

	if price:
		return client.orders.orders_limit_order_post(figi, {
			'price': price,
			'lots': count,
			'operation': 'Buy',
		}).payload

	else:
		hour = (int(time.strftime("%H")) + TIME_OFFSET) % 24 # Нельзя делать рыночные заявки на америнских акциях после 23:00
		# TODO: переделать на лимитные заявки

		if hour >= 10 and hour < 23:
			return client.orders.orders_market_order_post(figi, {
				'lots': count,
				'operation': 'Buy',
			}).payload

		else:
			price = get_price_by_ticker(ticker, 0, False)

			return client.orders.orders_limit_order_post(figi, {
				'price': price,
				'lots': count,
				'operation': 'Buy',
			}).payload

# Sell share
# TODO: min lots, min price_increment

def shares_sell(ticker, count, price=None): # TODO: стилизация
	figi = get_figi_by_ticker(ticker)

	if price:
		return client.orders.orders_limit_order_post(figi, {
			'price': price,
			'lots': count,
			'operation': 'Sell',
		}).payload

	else:
		hour = (int(time.strftime("%H")) + TIME_OFFSET) % 24 # Нельзя делать рыночные заявки на америнских акциях после 23:00

		if hour >= 10 and hour < 23:
			return client.orders.orders_market_order_post(figi, {
				'lots': count,
				'operation': 'Sell',
			}).payload

		else:
			price = get_price_by_ticker(ticker, 1, False)

			return client.orders.orders_limit_order_post(figi, {
				'price': price,
				'lots': count,
				'operation': 'Sell',
			}).payload