import requests

# payload = {
#     'content': 'asd',
# }

# headers = {
#     'authorization': '',
# }

# r = requests.post('https://discord.com/api/v9/channels/1083764068562771968/messages', data=payload, headers=headers)


# payload = {
#     "type":2,
#     "application_id":"936929561302675456",
#     # "guild_id":"667320783579774977",
#     "channel_id":"1069126859100524575",
#     "session_id":"",
#     "data": {
#         "version":"1077969938624553050",
#         "id":"938956540159881230",
#         "name":"imagine",
#         "type":1,
#         "options": [{
#             "type": 3,
#             "name": "prompt",
#             "value":"from bot",
#         }],
#         "application_command": {
#             "id":"938956540159881230",
#             "application_id":"936929561302675456",
#             "version":"1077969938624553050",
#             "default_permission":True,
#             "default_member_permissions":None,
#             "type":1,
#             "nsfw":False,
#             "name":"imagine",
#             "description":"Create images with Midjourney",
#             "dm_permission":True,
#             "options":[{
#                 "type":3,
#                 "name":"prompt",
#                 "description":"The prompt to imagine",
#                 "required":True,
#             }],
#         },
#         "attachments":[],
#     },
#     "nonce":"1083793667426091008",
# }

# payload = {"type":2,"application_id":"936929561302675456","channel_id":"1069126859100524575","session_id":"","data":{"version":"1077969938624553050","id":"938956540159881230","name":"imagine","type":1,"options":[{"type":3,"name":"prompt","value":"repeat"}],"application_command":{"id":"938956540159881230","application_id":"936929561302675456","version":"1077969938624553050","default_permission":True,"default_member_permissions":None,"type":1,"nsfw":False,"name":"imagine","description":"Create images with Midjourney","dm_permission":True,"options":[{"type":3,"name":"prompt","description":"The prompt to imagine","required":True}]},"attachments":[]},"nonce":"1083794641171513344"}
prompt="from bot"
payload = {
    "type":2,
    "application_id":"936929561302675456",
    # "guild_id":Globals.SERVER_ID,
    "channel_id": "1069126859100524575",
    "session_id":"",
    "data":{"version":"1077969938624553050",
            "id":"938956540159881230",
            "name":"imagine",
            "type":1,
            "options":[{"type":3,"name":"prompt","value":prompt}],
            "application_command":{
                "id":"938956540159881230",
                "application_id":"936929561302675456",
                "version":"1077969938624553050",
                "default_permission":True,
                "default_member_permissions":None,
                "type":1,
                "name":"imagine",
                "description":"There are endless possibilities...",
                "dm_permission":True,
                "options":[{"type":3,"name":"prompt","description":"The prompt to imagine","required":True}]},
                "attachments":[]}
}
user_token = ''
# headers = {
#     'authorization': '',
# }
headers = {
    'Authorization': user_token, # f'Bearer {user_token}',
    # 'Content-Type': 'application/json',
}

r = requests.post('https://discord.com/api/v9/interactions', json=payload, headers=headers)
print(r.text)



# curl 'https://discord.com/api/v9/interactions' \
#   -H 'authority: discord.com' \
#   -H 'accept: */*' \
#   -H 'accept-language: ru,en;q=0.9' \
#   -H 'authorization: ...' \
#   -H 'cache-control: no-cache' \
#   -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundaryumdtakAsWobEoKBn' \
#   -H 'cookie: __dcfduid=bcd31ce0471911ed8ce403810208b20c; __sdcfduid=bcd31ce1471911ed8ce403810208b20ca20f468570ee39f4c7e8816203c0430bacb68c4b3fb93c18f47b74eac65320b9; _gcl_au=1.1.2068837318.1678201231; locale=ru; __cfruid=cfa69c30ea83a4f7cfff46cc7c024a498e8654ba-1678432782; _gid=GA1.2.1215662139.1678454779; _ga=GA1.1.403083595.1678201201; OptanonConsent=isIABGlobal=false&datestamp=Fri+Mar+10+2023+20%3A26%3A19+GMT%2B0700+(Indochina+Time)&version=6.33.0&hosts=&landingPath=https%3A%2F%2Fdiscord.com%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1; _ga_Q149DFWHT7=GS1.1.1678454779.3.0.1678454791.0.0.0; __cf_bm=BbTH0l8RStWRs88QKYxe8w6zypLeF8b_Qung9rJ6aOQ-1678467094-0-ASEBBLfU+GImi2sfvxIm6WUEt8zriugLLbgMR5dOr1pdV99wGHp4FMsA8vVQcL8N/ncuE56c97rUXEbQrP85B7fsWz+23SyQqWFthmGyRWlCFQF4Ej/q/j7L6f80Qw5wpA==' \
#   -H 'origin: https://discord.com' \
#   -H 'pragma: no-cache' \
#   -H 'referer: https://discord.com/channels/@me/1069126859100524575' \
#   -H 'sec-ch-ua: "Not?A_Brand";v="8", "Chromium";v="108", "Yandex";v="23"' \
#   -H 'sec-ch-ua-mobile: ?0' \
#   -H 'sec-ch-ua-platform: "macOS"' \
#   -H 'sec-fetch-dest: empty' \
#   -H 'sec-fetch-mode: cors' \
#   -H 'sec-fetch-site: same-origin' \
#   -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 YaBrowser/23.1.2.980 Yowser/2.5 Safari/537.36' \
#   -H 'x-debug-options: bugReporterEnabled' \
#   -H 'x-discord-locale: ru' \
#   -H 'x-super-properties: eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IkNocm9tZSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJydSIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMDguMC4wLjAgWWFCcm93c2VyLzIzLjEuMi45ODAgWW93c2VyLzIuNSBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTA4LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwLjE1LjciLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiaHR0cHM6Ly93d3cueWFuZGV4LnJ1L2NsY2svanNyZWRpcj9mcm9tPXlhbmRleC5ydTtzdWdnZXN0O2Jyb3dzZXImdGV4dD0iLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiJ3d3cueWFuZGV4LnJ1IiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTc5NzE4LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJkZXNpZ25faWQiOjB9' \
#   --data-raw $'------WebKitFormBoundaryumdtakAsWobEoKBn\r\nContent-Disposition: form-data; name="payload_json"\r\n\r\n{"type":2,"application_id":"936929561302675456","channel_id":"1069126859100524575","session_id":"83c36685f2f85263b3622ceccb5fa03c","data":{"version":"1077969938624553050","id":"938956540159881230","name":"imagine","type":1,"options":[{"type":3,"name":"prompt","value":"repeat"}],"application_command":{"id":"938956540159881230","application_id":"936929561302675456","version":"1077969938624553050","default_permission":true,"default_member_permissions":null,"type":1,"nsfw":false,"name":"imagine","description":"Create images with Midjourney","dm_permission":true,"options":[{"type":3,"name":"prompt","description":"The prompt to imagine","required":true}]},"attachments":[]},"nonce":"1083794641171513344"}\r\n------WebKitFormBoundaryumdtakAsWobEoKBn--\r\n' \
#   --compressed