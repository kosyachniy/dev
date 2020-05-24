import time
import json
import requests

from binance.client import Client


with open('keys.json', 'r') as file:
	keys = json.loads(file.read())['binance']

client = Client(keys['key'], keys['secret'])


rub = lambda: float(requests.get('https://blockchain.info/tobtc?currency=RUB&value=1000').text) / 1000
btc_to_rub = lambda btc: int(btc/rub())


# Market depth / Order book (Стакан)

depth = client.get_order_book(symbol='BNBBTC')
print(depth)

# Trade websocket (Realtime курс)

def process_message(msg):
	if msg['e'] != 'aggTrade':
		print(msg)
		return

	price = float(msg['p'])
	quantity = float(msg['q'])

	print('{}	{}	V{}		{}₽'.format(time.ctime(msg['T']/1000), price, quantity, btc_to_rub(price*quantity)))

from binance.websockets import BinanceSocketManager
bm = BinanceSocketManager(client)
bm.start_aggtrade_socket('BNBBTC', process_message)
bm.start()

# Historical kline data / Candlestick (История)

klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")
# Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC"
# Client.KLINE_INTERVAL_1WEEK, "1 Jan, 2017"

for line in klines:
	price_open = float(line[1])
	price_high = float(line[2])
	price_low = float(line[3])
	price_close = float(line[4])
	volume = float(line[5])

	print('{}	OPEN {}	HIGH {}	LOW {}	CLOSE {}		V{}'.format(time.ctime(line[0]/1000), price_open, price_high, price_low, price_close, volume))

# # place a test market buy order, to place an actual order use the create_order function
# order = client.create_test_order(
#     symbol='BNBBTC',
#     side=Client.SIDE_BUY,
#     type=Client.ORDER_TYPE_MARKET,
#     quantity=100)

# # get all symbol prices
# prices = client.get_all_tickers()