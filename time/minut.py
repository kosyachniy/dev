from time import gmtime, mktime

minut = lambda: int(mktime(gmtime()) // 60)

if __name__ == '__main__':
	print(minut())