import requests

model = 'ruwikiruscorpora'

def rusvectores(word):
	try:
		if len(word) == 1:
			x = requests.get('http://rusvectores.org/%s/%s/api/json' % (model, word[0])).json()[model]
			for i in x:
				l = [[x[i][j], j] for j in x[i]]
				l.sort()
				return l[::-1]
		elif len(word) == 2:
			return float(requests.get('http://rusvectores.org/%s/%s__%s/api/similarity/' % (model, *word)).text.split()[0])
		else:
			return 0
	except:
		return 0

if __name__ == '__main__':
	x = rusvectores(input().split('-'))
	if type(x) == list:
		for i in x:
			print(i[0], '	', i[1].split('_')[0])
	else:
		print(x)