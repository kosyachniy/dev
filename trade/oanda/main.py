import requests, json

with open('set.txt', 'r') as file:
    key = json.loads(file.read())
    accountid = key['accountid']
    token = key['token']
print(accountid, token)

def connect_to_stream():
    try:
        s = requests.Session()
        url = 'https://stream-fxpractice.oanda.com/v1/prices' #https://api-fxtrade.oanda.com/v1/accounts
        headers = {'Authorization' : 'Bearer ' + token} #, 'X-Accept-Datetime-Format' : 'unix'
        params = {'instruments' : 'EUR_USD,AUD_JPY', 'accountId' : accountid}
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

print(connect_to_stream())