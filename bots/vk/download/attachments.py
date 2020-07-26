import os, json, re
from urllib.request import urlopen

def download(url, typ, rewrite = False):
	start = url.index('.com/')
	name = 'data/' + typ + '/' + url[start+5:].replace('/', '-')

	if not os.path.exists(name) or rewrite:
		try:
			resource = urlopen(url)
		except:
			print('Не существует!', url)
			return 1 #raise False

		out = open(name, 'wb')
		out.write(resource.read())
		out.close()
		return 1

	return 0

def attachments(url):
	previous = [] #Закачать предыдущее ещё раз, если было аварийно закончено и повреждено
	last = 0
	for i in os.listdir(url):
		if '-' not in i: continue

		with open(url+i, 'r') as file:
			messages = json.loads(file.read())

		for mes in messages:
			if 'attachments' in mes:
				for attachment in mes['attachments']:
					next_ = ()
					if attachment['type'] == 'image':
						next_ = (attachment['url'], 'images')
					elif attachment['type'] == 'document':
						next_ = (attachment['url'], 'documents')
					elif attachment['type'] == 'voice':
						next_ = (attachment['url'], 'voices')
					elif attachment['type'] == 'sticker':
						next_ = (attachment['url'], 'stickers')

					if len(next_):
						new_ = download(*next_)

						if last > new_:
							print(previous)
							if len(previous):
								download(previous[0], previous[1], True)
						previous = next_
						last = new_

if __name__ == '__main__':
	for i in ('data/dialogs/', 'data/chats/'):
		attachments(i)