import json
import time

from openapi_client import openapi
from datetime import datetime, timedelta
from pytz import timezone


with open('keys.json', 'r') as file:
	token = json.loads(file.read())['tinkoff']['token']


client = openapi.sandbox_api_client(token)


# Get stocks

def get_stocks(currency='USD'):
	stocks = client.market.market_stocks_get().payload.instruments

	stocks_processed = [{
		'name': i.name,
		'figi': i.figi,
		'ticker': i.ticker,
	} for i in stocks if i.currency == currency]

	return stocks_processed

# Get FIGI by ticker

def get_figi_by_ticker(name):
	ticker = client.market.market_search_by_ticker_get(name).payload.instruments

	if len(ticker) != 1:
		raise Exception('not found')

	return ticker[0].figi

# Get price by ticker

def get_price_by_ticker(name):
	figi = get_figi_by_ticker(name)
	prices = client.market.market_orderbook_get(figi, 2).payload
	return prices.asks[0], prices.bids[0]

# Get graph by ticker

def get_graph_by_ticker(name, start):
	figi = get_figi_by_ticker(name)
	# finish = datetime.now(tz=timezone('Europe/Moscow'))
	# start = finish - timedelta(days=1)
	# start1 = start - timedelta(days=1)
	# start2 = start1 - timedelta(days=1)
	start = datetime.fromtimestamp(start, tz=timezone('Europe/Moscow'))
	start1 = start + timedelta(days=1)
	start2 = start1 + timedelta(days=1)
	finish = start2 + timedelta(days=1)

	candles = client.market.market_candles_get(figi, start.isoformat(), start1.isoformat(), '1min').payload.candles
	candles += client.market.market_candles_get(figi, start1.isoformat(), start2.isoformat(), '1min').payload.candles
	candles += client.market.market_candles_get(figi, start2.isoformat(), finish.isoformat(), '1min').payload.candles

	return [candle.c for candle in candles]

# Get graph by FIGI

def get_graph_by_figi(figi, start=1577826000):
	start = datetime.fromtimestamp(start, tz=timezone('Europe/Moscow'))
	candles = []
	time_now = datetime.now(tz=timezone('Europe/Moscow'))

	while True:
		finish = start + timedelta(weeks=1)

		candles_period = client.market.market_candles_get(figi, start.isoformat(), finish.isoformat(), 'hour').payload.candles
		candles += [{
			'price': candle.c,
			'time': candle.time.timestamp(), # datetime.fromisoformat(candle.time).timestamp(),
		} for candle in candles_period]

		if finish >= time_now:
			break

		start, finish = finish, 0

	return candles

def get_graph_by_ticker2(name, start, time_finish=None):
	figi = get_figi_by_ticker(name)

	start = datetime.fromtimestamp(start, tz=timezone('Europe/Moscow'))
	candles = []

	if time_finish:
		time_finish = datetime.fromtimestamp(time_finish, tz=timezone('Europe/Moscow'))
	else:
		time_finish = datetime.now(tz=timezone('Europe/Moscow'))

	while True:
		finish = start + timedelta(weeks=1)

		candles_period = client.market.market_candles_get(figi, start.isoformat(), finish.isoformat(), 'hour').payload.candles # 15min
		candles += [{
			'price': candle.o,
			'time': candle.time.timestamp(), # datetime.fromisoformat(candle.time).timestamp(),
		} for candle in candles_period]

		if finish >= time_finish:
			break

		start, finish = finish, 0

	return candles