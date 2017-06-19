import re, requests

def cut(s,st1,st2,ex,en):
	l=list()
	while s.find(st1)+1:
		s=s[s.find(st1)+len(st1):]
		if st2:
			s=s[s.find(st2)+len(st2):]
		s=s[ex:]
		mi=s.find(en[0])
		for i in en:
			if s.find(i)<mi:
				mi=s.find(i)
		l.append(re.sub(r'\<[^>]*\>','',s[:mi]))
	return l

if __name__=='__main__':
	for i in cut(requests.get('https://market.yandex.ru/catalog/54726/list?text='+input('Продукт: ')).text,'snippet-cell__header','href="/product/',0,('?','/')):
		print('https://market.yandex.ru/product/'+i)