import apiai, json

with open('keys.json', 'r') as file:
	token_dialogflow = json.loads(file.read())['token_dialogflow']

def answer(text):
	request = apiai.ApiAI(token_dialogflow).text_request()
	request.lang = 'ru'
	request.session_id = 'BatlabAIBot'
	request.query = text
	response_json = json.loads(request.getresponse().read().decode('utf-8'))
	print(response_json)
	print('-'*100)
	return response_json['result']['fulfillment']['speech']

if __name__ == '__main__':
	print(answer(input()))
