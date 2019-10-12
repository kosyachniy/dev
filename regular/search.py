import re


cont = '<bla id="123">'

res = int(re.search(r'id="[0-9]*"', cont).group(0)[4:-1])

print(res)