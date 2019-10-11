import requests


def get(src, headers={}, params={}):
	return requests.get(src, headers=headers, params=params).text


if __name__=='__main__':
	print(get(input()))