import requests

def get(src):
	return requests.get(src).text

if __name__=='__main__':
	print(get(input()))