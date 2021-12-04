import requests


def get(src, headers={}, params={}, data={}, json={}, files={}):
	return requests.get(src, headers=headers, params=params, data=data, json=json, files=files).text

def post(src, headers={}, params={}, data={}, json={}, files={}):
	return requests.post(src, headers=headers, params=params, data=data, json=json, files=files).text


if __name__=='__main__':
	print(get(input()))
