with open('...', 'rb') as file:
	files = {'media': file.read()}

cont = requests.post('http://...', json = {"param1": num, "param2": "text"}, files = files)
print(cont)