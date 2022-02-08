import re
import ssl
import shutil
import urllib

import requests


LINK = input("Ссылка: ")
PREFIX = input("Префикс: ")
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': '__bp=...; _ym_uid=...; _ym_d=...; _ym_isad=...',
    'Host': 's22.stream.bizon365.ru',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Yandex";v="22"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 YaBrowser/22.1.0.2500 Yowser/2.5 Safari/537.36',
}


data1 = requests.get(LINK, headers=HEADERS).text

file1 = f'data/{PREFIX}/' + LINK.split('/')[-1].split('?')[0]
with open(file1, 'w') as file:
    print(data1, file=file)

LINK = '/'.join(LINK.split('/')[:3])

options = re.findall(r'#EXT-X-STREAM-INF:[\w=]*,RESOLUTION=[^x]*x(\d*),', data1)
max_option = max(map(int, options))
print(f"Разрешение: {max_option}p")

link = re.findall((
    rf'#EXT-X-STREAM-INF:[\w="]*,'
    rf'RESOLUTION=[^x]*x{max_option},'
    rf'[\w="]*\n([^\n]*)\n'
), data1)[0]
link = f'{LINK}{link}'
# print(link)

data2 = requests.get(link, headers=HEADERS).text
# print(data2)

file2 = link.split('/')[-1].split('?')[0] # re.findall(rf'{max_option}[\w.]*\.m3u8', x)[0]
with open(f'data/{PREFIX}/{file2}', 'w') as file:
    print(data2, file=file)

fragments = re.findall(r'\n([^\n]*\.ts[^\n]*)\n', data2)
base_link = '/'.join(link.split('/')[:-1])
context = ssl._create_unverified_context()

for i, fragment in enumerate(fragments):
    # print(fragment)

    req = urllib.request.Request(f'{base_link}/{fragment}')
    for header in HEADERS:
        req.add_header(header, HEADERS[header])

    file3 = fragment.split('?')[0]

    with urllib.request.urlopen(req, context=context) as response:
        with open(f'data/{PREFIX}/{file3}', 'wb') as tmp_file:
            shutil.copyfileobj(response, tmp_file)

    print(f"✅ Фрагмент №{i+1}")
