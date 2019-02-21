import json
from func import read

with open('data/db.json', 'r') as file:
	texts = [i['text'] for i in json.loads(file.read())]

main_words = read('formated')
#vector_words = read('table')

for i, sentence in enumerate(texts):
	if sentence:
		print('"%s" - "%s"' % (sentence, ' '.join(main_words[i]))) # - %s #, ' '.join(vector_words[i])