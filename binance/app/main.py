import os
import sys
import json

import requests


BINANCE_ID = os.getenv('BINANCE_ID')
BINANCE_SECRET = os.getenv('BINANCE_SECRET')
LINK = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Length": "123",
    "content-type": "application/json",
    "Host": "p2p.binance.com",
    "Origin": "https://p2p.binance.com",
    "Pragma": "no-cache",
    "TE": "Trailers",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
}


def get(crypto='USDT', currency='TRY', kind='SELL', amount=5000):
    try:
        data = json.loads(requests.post(
            LINK,
            headers=HEADERS,
            json={
                'asset': crypto,
                'fiat': currency,
                'merchantCheck': True,
                'page': 1,
                'payTypes': ['BANK'],
                'publisherType': None,
                'rows': 20,
                'tradeType': kind,
                'transAmount':  str(amount),
            },
        ).text)['data']

    except Exception as e:
        print(e)
        return None

    if not data or not isinstance(data, list):
        return None

    return data

def parse(data):
    if data['adv']['tradeType'] == 'BUY':
        kind = 0
    elif data['adv']['tradeType'] == 'SELL':
        kind = 1
    else:
        return None

    return {
        'type': kind,
        'crypto': data['adv']['asset'],
        'currency': data['adv']['fiatUnit'],
        'price': data['adv']['price'],
        'name': data['advertiser']['nickName'],
        'deals': data['advertiser']['monthOrderCount'],
        'success': data['advertiser']['monthFinishRate'],
    }


if __name__ == '__main__':
    data = get()
    if data is None:
        print('Error')
        sys.exit()

    data = parse(data[0])
    if data is None:
        print('Error')
        sys.exit()

    print(
        f"{data['crypto']} {'→←'[data['type']]} {data['currency']}"
        f" : {data['price']} {data['currency']}/{data['crypto']}"
        f"\n{data['name']} ({data['deals']}, {int(data['success'] * 100)}%)"
    )
    # with open('res.json', 'w') as file:
    #     print(json.dumps(data, indent="\t"), file=file)
