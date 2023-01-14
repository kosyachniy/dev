import re


def check_phone(cont):
	if cont[0] == '8':
		cont = '7' + cont[1:]

	cont = re.sub(r'[^0-9]', '', cont)

	if not len(cont):
		raise Exception('not phone')

	return int(cont)

def remove_tags(cont):
	return re.sub(r'<[^>]*>', '', cont)

def get_link(cont):
    return re.sub(r'.*<img src="([^"]*)">.*', r'\1', cont)


print(check_phone('8 (981) 163-55-78'))
print(get_link('<div class="react-mathjax-preview-result"><p>123</p><figure class="image image-style-side"><img src="https://tensy.s3.eu-central-1.amazonaws.com/prod/D47dg8OGKK3Yco897MhOIQ1Yzwi47XGZ."><figcaption>123</figcaption></figure><p>456</p><p>789</p><p>qwe</p><p>asd</p><p>zxc</p></div>'))