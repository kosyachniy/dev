from time import strptime, mktime

stamp = lambda x: int(mktime(strptime(x, '%d.%m.%Y %H:%M:%S')))

if __name__ == '__main__':
	print(stamp('30.11.2017 22:00:58'))