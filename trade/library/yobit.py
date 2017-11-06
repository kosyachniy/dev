"""
    See https://yobit.net/en/api/
"""

import time
import hmac
import hashlib
import json
try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode
    from urllib.parse import urljoin
import requests

BASE_PUBLIC = 'https://yobit.net/api/3/'
BASE_TRADE = 'https://yobit.net/tapi'


def refactor_result(json_ob):
    return json.dumps(json_ob, sort_keys=True, indent=4, separators=(',', ': '))


class YoBit(object):
    with open('data/set.txt', 'r') as file:
    	key, secret = json.loads(file.read())['yobit']

    def __init__(self, api_key=key, api_secret=secret):
        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''
        if api_key == '' or api_secret == '':
            print('mode: PublicAPI')
        else:
            print('mode: PublicAPI & TradeAPI')

    @staticmethod
    def __api_query_public(method, pair=None, options=None):
        """
        Queries YoBit Public API with given method, pair and options.

        :param method: Query method for getting info from Public API
        :type method: str

        :param pair: Pair of currencies, example 'ltc_btc'
        :type pair: str

        :param options: Extra options for query
        :type options: dict

        :return: JSON response from YoBit Public API
        :rtype : dict
        """
        if not options:
            options = {}
        if not pair:
            pair = ''

        request_url = BASE_PUBLIC + method
        if pair != '':
            request_url += '/' + pair.lower()
        if options != {}:
            request_url += '?'
            request_url += urlencode(options)

        return requests.get(request_url).json()

    def __api_query_trade(self, method, options=None):
        """
        Queries YoBit Trade API with given method and options.

        :param method: Query method  for getting info from Trade API
        :type method: str

        :param options: Extra options for query
        :type options: dict

        :return: JSON response from YoBit Trade API
        :rtype : dict
        """
        if not options:
            options = {}

        request_url = BASE_TRADE
        options['method'] = method
        options['nonce'] = str(int(time.time()))

        body = urlencode(options)

        signature = hmac.new(self.api_secret.encode(), body.encode(), hashlib.sha512).hexdigest()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Key': self.api_key,
            'Sign': signature
        }

        return requests.post(request_url, data=options, headers=headers).json()

    def info(self):
        """
        Used to get about server time and coin pares of the YoBit market.
        Response contains min_price, max_price, min_amount, and fee for each pair.

        :return: JSON of pairs with info
        :rtype : dict
        """
        return self.__api_query_public('info')

    def ticker(self, pair):
        """
        Used to get statistic data for the last 24 hours for selected pair.
        Response contains hight, low, avg, vol, vol_cur, last, buy, sell fields for the pair.

        :param pair: Pair of currencies, example 'ltc_btc'
        :type pair: str

        :return: Statistic
        :rtype : dict
        """
        return self.__api_query_public('ticker', pair)

    def depth(self, pair, limit=150):
        """
        Used to get information about lists of active orders for selected pair.
        Response contains asks and bids lists for the pair.

        :param pair: Pair of currencies, example 'ltc_btc'
        :type pair: str

        :param limit: Size of response (on default 150 to 2000 max)
        :type limit: int

        :return: Current information about active orders
        :rtype : dict
        """
        return self.__api_query_public('depth', pair, {'limit': limit})

    def trades(self, pair, limit=150):
        """
        Used to get information about the last transactions of selected pair.
        Response contains type, price, amount, tid, timestamp for each transaction.

        :param pair: Pair of currencies, example 'ltc_btc'
        :type pair: str

        :param limit: Size of response (on default 150 to 2000 max)
        :type limit: int

        :return: Current information about transactions
        :rtype : dict
        """
        return self.__api_query_public('trades', pair, {'limit': limit})

    def get_info(self):
        """
        Used to get information about user's balances and priviledges of API-key
        as well as server time. Response contains funds, fund_incl_orders, rights,
        transaction_count, open_orders, server time.

        :return: JSON with info
        :rtype : dict
        """
        return self.__api_query_trade('getInfo')

    def trade(self, pair, trade_type, rate, amount):
        """
        Used to create new orders for stock exchange trading

        :param pair: Pair of currencies, example 'ltc_btc'
        :type pair: str

        :param trade_type: 'buy' or 'sell'
        :type trade_type: str

        :param rate: Exchange rate for buying or selling
        :type rate: float

        :param amount: Amount of needed for buying or selling
        :type amount: float

        :return: Success, info about the order, order_id.
        :rtype : dict
        """
        return self.__api_query_trade('Trade', {'pair': pair, 'type': trade_type, 'rate': rate, 'amount': amount})

    def active_orders(self, pair):
        """
        Used to get list of user's active orders.

        :param pair: Pair of currencies, example 'ltc_btc'
        :type pair: str

        :return: List of orders byu order_id
        :rtype : dict
        """
        return self.__api_query_trade('ActiveOrders', {'pair': pair})

    def order_info(self, order_id):
        """
        Used to get detailed information about the chosen order.
        Response contains pair, type, start_amount, amount, rate,
        timestamp_created, status for the order.

        :param order_id: Order ID
        :type order_id: int

        :return: JSON of the order
        :rtype : dict
        """
        return self.__api_query_trade('OrderInfo', {'order_id': order_id})

    def cancel_order(self, order_id):
        """
        Used to cancel the choosen order.

        :param order_id: Order ID
        :type order_id: int

        :return: Success and balances active after request
        :rtype : dict
        """
        return self.__api_query_trade('CancelOrder', {'order_id': order_id})

    def trade_history(self, pair, from_start=0, count=1000, from_id=0, end_id=100000000000,
                      order='DESC', since=0, end=time.time() + 1000):
        """
        Used to retrieve transaction history.
        Response contains list of transactions with pair, type,
        amount, rate, order_id, is_your_order and timestamp for each transaction.

        :param pair: Pair of currencies, example 'ltc_btc'
        :type pair: str

        :param from_start: Number of transaction from which response starts (default 0)
        :type from_start: int

        :param count: Quantity of transactions in response (default 1000)
        :type count: int

        :param from_id: ID of transaction from which response start (default 0)
        :type from_id: int

        :param end_id: ID of trnsaction at which response finishes (default inf)
        :type end_id: int

        :param order: Sorting order, 'ASC' for ascending and 'DESC' for descending
        :type order: str

        :param since: The time to start the display (unix time, default 0)
        :type since: int

        :param end: The time to end the display (unix time, default inf)
        :type end: int

        :return: List of transactions
        :rtype : dict
        """
        options = {
            'from': from_start,
            'count': count,
            'from_id': from_id,
            'end_id': end_id,
            'order': order,
            'since': since,
            'end': end,
            'pair': pair
        }
        return self.__api_query_trade('TradeHistory', options)

    def get_deposit_address(self, coin_name, need_new=False):
        """
        Used to get deposit address.

        :param coin_name: The name of a coin, example 'BTC'
        :type coin_name: str

        :param need_new: True or False
        :type need_new: bool

        :return: Wallet address
        :rtype : dict
        """
        options = {'coinName': coin_name, 'need_new': 1 if need_new else 0}
        return self.__api_query_trade('GetDepositAddress', options)

    def withdraw_coins_to_address(self, coin_name, amount, address):
        """
        Used to create withdrawal request.

        :param coin_name: The name of a coin, example 'BTC'
        :type coin_name: str

        :param amount: Amount to withdraw
        :type amount: float

        :param address: Destination address
        :type address: str

        :return: Success and server time
        :rtype : dict
        """
        options = {'coinName': coin_name, 'amount': amount, 'address': address}
        return self.__api_query_trade('WithdrawCoinsAddress', options)