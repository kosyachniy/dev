from time import strptime, mktime, gmtime

now = lambda: mktime(gmtime()) // 60
stamp = lambda x: mktime(strptime(x, '%d.%m.%Y %H:%M:%S')) // 60

print(int(now() - stamp('30.11.2017 22:00:58')))