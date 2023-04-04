import requests
import json

# Replace `USER_TOKEN` with the token of the user account you want to use
user_token = ''

# Replace `BOT_ID` with the ID of the bot you want to send a message to
bot_id = ''

# Replace `MESSAGE` with the message you want to send to the bot
message = 'asd123'

# Set the HTTP headers and payload
headers = {
    'Authorization': user_token, # f'Bearer {user_token}',
    'Content-Type': 'application/json',
}
payload = {
    'content': message
}

# r = requests.get(f'https://discord.com/api/v9/channels/1069126859100524575/messages', headers=headers)
# response = requests.post(f'https://discord.com/api/users/@me/channels', headers=headers, json={'recipient_id': bot_id})
# print(response.text)

# Send the message to the bot
response = requests.post(f'https://discord.com/api/users/@me/channels', headers=headers, json={'recipient_id': bot_id})
response_data = json.loads(response.content)
print('!', response_data)
channel_id = response_data['id']
response = requests.post(f'https://discord.com/api/channels/{channel_id}/messages', headers=headers, json=payload)

# Print the response status code and content
print(response.status_code)
print(json.loads(response.content))



# curl 'https://discord.com/api/v9/channels/1069126859100524575/messages' \
#   -H 'authorization: ...'



#   -H 'authority: discord.com' \
#   -H 'accept: */*' \
#   -H 'accept-language: ru,en;q=0.9' \
#   -H 'authorization: ...' \
#   -H 'cache-control: no-cache' \
#   -H 'cookie: __dcfduid=bcd31ce0471911ed8ce403810208b20c; __sdcfduid=bcd31ce1471911ed8ce403810208b20ca20f468570ee39f4c7e8816203c0430bacb68c4b3fb93c18f47b74eac65320b9; _gcl_au=1.1.2068837318.1678201231; locale=ru; _gid=GA1.2.1215662139.1678454779; _ga=GA1.1.403083595.1678201201; OptanonConsent=isIABGlobal=false&datestamp=Fri+Mar+10+2023+20%3A26%3A19+GMT%2B0700+(Indochina+Time)&version=6.33.0&hosts=&landingPath=https%3A%2F%2Fdiscord.com%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1; _ga_Q149DFWHT7=GS1.1.1678454779.3.0.1678454791.0.0.0; __cfruid=883e3dc69f7063e29528e874cd28ef2ec530a1a4-1678467965; __cf_bm=j6hikmU7toazugU1C6cBIk89z4k_kIdJ3WLp2oNZhMc-1678469484-0-AYXoRll8V7U3WvlPfocWodldVjDXJ/Cur7OnAqq+Eo3pyMJVtMbHsXMRnVUX7RfenSoj39Fwds5CIcO5f0Y1ND+xLPOUAe0fe/PaPvNOP3dV/3dYTSUwMlOSZDuL9xXslg==' \
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
#   --compressed







# curl 'https://discord.com/api/v9/interactions' \
#   -H 'authority: discord.com' \
#   -H 'accept: */*' \
#   -H 'accept-language: ru,en;q=0.9' \
#   -H 'authorization: ...' \
#   -H 'cache-control: no-cache' \
#   -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary9XyJLefASdA2YIoI' \
#   -H 'cookie: __dcfduid=bcd31ce0471911ed8ce403810208b20c; __sdcfduid=bcd31ce1471911ed8ce403810208b20ca20f468570ee39f4c7e8816203c0430bacb68c4b3fb93c18f47b74eac65320b9; _gcl_au=1.1.2068837318.1678201231; locale=ru; _gid=GA1.2.1215662139.1678454779; _ga=GA1.1.403083595.1678201201; OptanonConsent=isIABGlobal=false&datestamp=Fri+Mar+10+2023+20%3A26%3A19+GMT%2B0700+(Indochina+Time)&version=6.33.0&hosts=&landingPath=https%3A%2F%2Fdiscord.com%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1; _ga_Q149DFWHT7=GS1.1.1678454779.3.0.1678454791.0.0.0; __cfruid=883e3dc69f7063e29528e874cd28ef2ec530a1a4-1678467965; __cf_bm=J0hNa.5CIHkTCHudGIBWL28XjBhQvhTNRzCILfVOTZA-1678470725-0-AZZwGv+rZahtRAkNIttNnDP8ceSYldxuqneIeUz4vGJkAODm6BbLfHlYtz8eWLXpGd7wk/7i3TXlVPWE+i+kMjAXaUnGRwcyXqmgHbGDUTZnJSW4A9mX0WIBrNqFdx7bHA==' \
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
#   --data-raw $'------WebKitFormBoundary9XyJLefASdA2YIoI\r\nContent-Disposition: form-data; name="payload_json"\r\n\r\n{"type":2,"application_id":"936929561302675456","channel_id":"1069126859100524575","session_id":"7687ebdc6846e1f686f02b14c4f150d1","data":{"version":"1077969938624553050","id":"938956540159881230","name":"imagine","type":1,"options":[{"type":3,"name":"prompt","value":"one more"}],"application_command":{"id":"938956540159881230","application_id":"936929561302675456","version":"1077969938624553050","default_permission":true,"default_member_permissions":null,"type":1,"nsfw":false,"name":"imagine","description":"Create images with Midjourney","dm_permission":true,"options":[{"type":3,"name":"prompt","description":"The prompt to imagine","required":true}]},"attachments":[]},"nonce":"1083811737217531904"}\r\n------WebKitFormBoundary9XyJLefASdA2YIoI--\r\n' \
#   --compressed
