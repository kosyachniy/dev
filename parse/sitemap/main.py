LINK = 'https://www.letu.ru/product/'


with open('letu.xml', 'r') as file:
    data = file.read()

print(data.count(LINK))
