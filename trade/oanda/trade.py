import requests, json
from urllib.parse import urlencode

with open('set.txt', 'r') as file:
    key = json.loads(file.read())
    accountid = key['accountid']
    token = key['token']

def order(instr, take_profit, stop_loss):
    try:
        s = requests.Session()
        url = 'https://api-fxpractice.oanda.com/v1/accounts/' + accountid + '/orders'

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
            #'accountId' : accountid
            })
                                    
        req = requests.post(url, data=params, headers=headers)
        for line in req.iter_lines(1):
            print("order responce: ", line)
    except Exception as e:
        print("Caught exception when connecting to orders\n" + str(e))

print(order('EUR_USD', 0.0001, 0.001))