import json

from openapi_client import openapi
from datetime import datetime, timedelta
from pytz import timezone


with open('keys.json', 'r') as file:
	token = json.loads(file.read())['tinkoff']['token']


client = openapi.sandbox_api_client(token)
client.sandbox.sandbox_register_post()
client.sandbox.sandbox_clear_post()
client.sandbox.sandbox_currencies_balance_post(sandbox_set_currency_balance_request={"currency": "USD", "balance": 1000})


def set_balance():
    balance_set = client.sandbox.sandbox_currencies_balance_post({"currency": "USD", "balance": 10000})
    print("balance")
    print(balance_set)
    print()

def get_balance():
	# balance_get = client.sandbox.sandbox_register_post()
	# balance_get = client.user.user_accounts_get()
	# balance_get = client.sandbox.sandbox_currencies_balance_post_with_http_info("USD") # {"currency": "USD"})
	# balance_get = client.sandbox.sandbox_currencies_balance_post({"currency": "USD", "balance": 10000})
	# sandbox_currencies_balance_post("USD") # {"currency": "USD"})
	# balance_get = client.market.market_currencies_get()
	# balance_get = client.market.market_orderbook_get("BBG000BLNNH6", 5)
	# balance_get = client.portfolio.portfolio_currencies_get()
	# balance_get = client.market.market_candles_get("BBG000BLNNH6")
	# balance_get = client.market.market_stocks_get()
	# balance_get = client.market.market_search_by_ticker_get("USD000UTSTOM")
	balance_get = client.market.market_search_by_ticker_get("WMT")
	# balance_get = client.market.market_candles_get("BBG0013HGFT4", 1588681858, 1589113837, "hour") # "2020-05-01T00:00:00.131642+03:00", "2020-05-10T00:00:00.131642+03:00", "hour") # 1min, 2min, 3min, 5min, 10min, 15min, 30min, hour, day, week, month
	# balance_get = client.market.market_candles_get("BBG0013HGFT4", "2020-05-01T00:00:00.131642+03:00", "2020-05-10T00:00:00.131642+03:00", "day") # "2020-05-01T00:00:00", "2020-05-10T00:00:00", "hour") # 1min, 2min, 3min, 5min, 10min, 15min, 30min, hour, day, week, month
	print("balance get")
	print(balance_get)
	print()

def get_price_by_ticker(name):
	ticker = client.market.market_search_by_ticker_get(name).payload.instruments

	if len(ticker) != 1:
		raise Exception('not found')

	figi = ticker[0].figi

	prices = client.market.market_orderbook_get(figi, 2).payload

	return prices.asks[0], prices.bids[0]

def print_24hr_operations():
    now = datetime.now(tz=timezone('Europe/Moscow'))
    yesterday = now - timedelta(days=1)
    ops = client.operations.operations_get(_from=yesterday.isoformat(), to=now.isoformat())
    print("operations")
    print(ops)
    print()


def print_orders():
    orders = client.orders.orders_get()
    print("active orders")
    print(orders)
    print()


def make_order():
    order_response = client.orders.orders_limit_order_post(figi='BBG009S39JX6',
                                                           limit_order_request={"lots": 1,
                                                                                "operation": "Buy",
                                                                                "price": 0.01})
    print("make order")
    print(order_response)
    print()
    return order_response


# won't work in sandbox - orders are being instantly executed
def cancel_order(order_id):
    cancellation_result = client.orders.orders_cancel_post(order_id=order_id)
    print("cancel order")
    print(cancellation_result)
    print()


# set_balance()
# print_24hr_operations()
# print_orders()
# order_response = make_order()
# print_orders()
# get_balance()
# cancel_order(order_response.payload.order_id)
# print_orders()
print(get_price_by_ticker('WMT'))