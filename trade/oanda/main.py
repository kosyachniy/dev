import requests
import json
from urllib.parse import urlencode


with open('keys.json', 'r') as file:
    keys = json.loads(file.read())
    accountid = keys['accountid']
    token = keys['token']

def connect_to_stream():
    try:
        s = requests.Session()
        url = 'https://api-fxpractice.oanda.com/v1/prices'
        headers = {'Authorization' : 'Bearer ' + token} #, 'X-Accept-Datetime-Format' : 'unix'
        params = {'instruments' : 'EUR_USD', 'accountId' : accountid} #EUR_USD
        req = requests.Request('GET', url, headers = headers, params = params)
        pre = req.prepare()
        resp = s.send(pre, stream=True, verify=False, timeout=20)
        return resp
    except Exception as e:
        s.close()
        print("Caught exception when connecting to stream\n" + str(e))

def read(response):
    try:
        for line in response.iter_lines(1):
            if line:
                msg = json.loads(line)         
                if msg.has_key("instrument") or msg.has_key("tick"): 
                    strategy(msg['tick']['instrument'], msg['tick']['time'], msg['tick']['ask'])
    except Exception as e:
        print("something gone bad " + str(e))
        return

def order(instr, take_profit, stop_loss):
    try:
        url = 'https://api-fxpractice.oanda.com/v1/accounts/' + accountid + '/orders'
        print(url)
        headers = {'Authorization' : 'Bearer ' + token,
                    #'X-Accept-Datetime-Format' : 'unix'
                    "Content-Type" : "application/x-www-form-urlencoded"
                  }
    
        params = urlencode({
            "instrument" : instr, #инструмент, по которому открывает сделку
            "units" : 10, #сколько единиц покупаем
            "type" : 'market', #прям сейчас исполнить!
            "side" : 'buy', #считаем, что цена пойдет вверх ("sell" если думаем что вниз)
            "takeProfit" : take_profit, #насколько цена должна пройти вверх, чтобы наша жадность удовлетворилась, и мы закрыли бы сделку. и считали профит
            "stopLoss" : stop_loss #насколько цена может опуститься, прежде чем наш страх скажет "ты чё?!! дальше только хуже будет. закрывай немедля. фиг с ними с потерями"
            })
                                    
        req = requests.post(url, data=params, headers=headers)
        for line in req.iter_lines(1):
            print("order responce: ", line)
    except Exception as e:
        print("Caught exception when connecting to orders\n" + str(e))

print(connect_to_stream().json())
print(order('EUR_USD', 0.0001, 0.001))