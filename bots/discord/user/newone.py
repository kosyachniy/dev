import websocket #pip install websocket-client
import json
import threading
import time

def send_json_request(ws, request):
    ws.send(json.dumps(request))

def recieve_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)

def heartbeat(interval, ws):
    print('Heartbeat begin')

    while True:
        time.sleep(interval)
        heartbeatJSON = {
            'op': 1,
            'd': 'null',
        }
        send_json_request(ws, heartbeatJSON)
        print("Heartbeat sent")

ws = websocket.WebSocket()
ws.connect('wss://gateway.discord.gg/?v=6&encording=json')
event = recieve_json_response(ws)

heartbeat_interval = event['d']['heartbeat_interval'] / 1000
threading._start_new_thread(heartbeat, (heartbeat_interval, ws))

token = ""
payload = {
    "op": 2,
    "d": {
        "token": token,
        "properties": {
            "$os": "windows",
            "$browser": "chrome",
            "$device": 'pc',
        }
    }
}
send_json_request(ws, payload)

while True:
    event = recieve_json_response(ws)
    try:
        if event['t'] == 'MESSAGE_CREATE':
            print(event)
        # print(f"{event['d']['author']['username']}: {event['d']['content']}")
        op_code = event('op')
        if op_code == 11:
            print('heartbeat received')
    except:
        pass


# {
#     "t": "MESSAGE_CREATE",
#     "s": 8,
#     "op": 0,
#     "d": {
#         "webhook_id": "936929561302675456",
#         "type": 0,
#         "tts": false,
#         "timestamp": "2023-03-10T16:29:14.383000+00:00",
#         "pinned": false,
#         "nonce": "1083788665919897600",
#         "mentions": [
#             {
#                 "username": "Alex Poloz",
#                 "public_flags": 0,
#                 "id": "439110225975443468",
#                 "display_name": null,
#                 "discriminator": "3841",
#                 "avatar_decoration": null,
#                 "avatar": "5b4b6129f485b13e6aa49411ff4391ee"
#             }
#         ],
#         "mention_roles": [],
#         "mention_everyone": false,
#         "interaction": {
#             "user": {
#                 "username": "Alex Poloz",
#                 "public_flags": 0,
#                 "id": "439110225975443468",
#                 "display_name": null,
#                 "discriminator": "3841",
#                 "avatar_decoration": null,
#                 "avatar": "5b4b6129f485b13e6aa49411ff4391ee"
#             },
#             "type": 2,
#             "name": "imagine",
#             "id": "1083788667513999500"
#         },
#         "id": "1083788668470304788",
#         "flags": 0,
#         "embeds": [],
#         "edited_timestamp": null,
#         "content": "**glass** - <@439110225975443468> (Waiting to start)",
#         "components": [],
#         "channel_id": "1069126859100524575",
#         "author": {
#             "username": "Midjourney Bot",
#             "public_flags": 65536,
#             "id": "936929561302675456",
#             "display_name": null,
#             "discriminator": "9282",
#             "bot": true,
#             "avatar_decoration": null,
#             "avatar": "4a79ea7cd151474ff9f6e08339d69380"
#         },
#         "attachments": [],
#         "application_id": "936929561302675456"
#     }
# }


# {
#     "t": "MESSAGE_CREATE",
#     "s": 14,
#     "op": 0,
#     "d": {
#         "type": 0,
#         "tts": false,
#         "timestamp": "2023-03-10T16:29:47.602000+00:00",
#         "referenced_message": null,
#         "pinned": false,
#         "mentions": [
#             {
#                 "username": "Alex Poloz",
#                 "public_flags": 0,
#                 "id": "439110225975443468",
#                 "display_name": null,
#                 "discriminator": "3841",
#                 "avatar_decoration": null,
#                 "avatar": "5b4b6129f485b13e6aa49411ff4391ee"
#             }
#         ],
#         "mention_roles": [],
#         "mention_everyone": false,
#         "id": "1083788807800897597",
#         "flags": 0,
#         "embeds": [],
#         "edited_timestamp": null,
#         "content": "**glass** - <@439110225975443468> (relaxed)",
#         "components": [
#             {
#                 "type": 1,
#                 "components": [
#                     {
#                         "type": 2,
#                         "style": 2,
#                         "label": "U1",
#                         "custom_id": "MJ::JOB::upsample::1::a7cb1552-f779-4094-9afe-2acf22dae280"
#                     },
#                     {
#                         "type": 2,
#                         "style": 2,
#                         "label": "U2",
#                         "custom_id": "MJ::JOB::upsample::2::a7cb1552-f779-4094-9afe-2acf22dae280"
#                     },
#                     {
#                         "type": 2,
#                         "style": 2,
#                         "label": "U3",
#                         "custom_id": "MJ::JOB::upsample::3::a7cb1552-f779-4094-9afe-2acf22dae280"
#                     },
#                     {
#                         "type": 2,
#                         "style": 2,
#                         "label": "U4",
#                         "custom_id": "MJ::JOB::upsample::4::a7cb1552-f779-4094-9afe-2acf22dae280"
#                     },
#                     {
#                         "type": 2,
#                         "style": 2,
#                         "emoji": {
#                             "name": "\ud83d\udd04"
#                         },
#                         "custom_id": "MJ::JOB::reroll::0::a7cb1552-f779-4094-9afe-2acf22dae280::SOLO"
#                     }
#                 ]
#             },
#             {
#                 "type": 1,
#                 "components": [
#                     {
#                         "type": 2,
#                         "style": 2,
#                         "label": "V1",
#                         "custom_id": "MJ::JOB::variation::1::a7cb1552-f779-4094-9afe-2acf22dae280"
#                     },
#                     {
#                         "type": 2,
#                         "style": 2,
#                         "label": "V2",
#                         "custom_id": "MJ::JOB::variation::2::a7cb1552-f779-4094-9afe-2acf22dae280"
#                     },
#                     {
#                         "type": 2,
#                         "style": 2,
#                         "label": "V3",
#                         "custom_id": "MJ::JOB::variation::3::a7cb1552-f779-4094-9afe-2acf22dae280"
#                     },
#                     {
#                         "type": 2,
#                         "style": 2,
#                         "label": "V4",
#                         "custom_id": "MJ::JOB::variation::4::a7cb1552-f779-4094-9afe-2acf22dae280"
#                     }
#                 ]
#             }
#         ],
#         "channel_id": "1069126859100524575",
#         "author": {
#             "username": "Midjourney Bot",
#             "public_flags": 65536,
#             "id": "936929561302675456",
#             "display_name": null,
#             "discriminator": "9282",
#             "bot": true,
#             "avatar_decoration": null,
#             "avatar": "4a79ea7cd151474ff9f6e08339d69380"
#         },
#         "attachments": [
#             {
#                 "width": 1024,
#                 "url": "https://cdn.discordapp.com/attachments/1069126859100524575/1083788807381471404/Alex_Poloz_glass_a7cb1552-f779-4094-9afe-2acf22dae280.png",
#                 "size": 1249332,
#                 "proxy_url": "https://media.discordapp.net/attachments/1069126859100524575/1083788807381471404/Alex_Poloz_glass_a7cb1552-f779-4094-9afe-2acf22dae280.png",
#                 "id": "1083788807381471404",
#                 "height": 1024,
#                 "filename": "Alex_Poloz_glass_a7cb1552-f779-4094-9afe-2acf22dae280.png",
#                 "content_type": "image/png"
#             }
#         ]
#     }
# }









# curl 'https://discord.com/api/v9/interactions' \
#   -H 'authority: discord.com' \
#   -H 'accept: */*' \
#   -H 'accept-language: ru,en;q=0.9' \
#   -H 'authorization: ...' \
#   -H 'cache-control: no-cache' \
#   -H 'content-type: application/json' \
#   -H 'cookie: __dcfduid=bcd31ce0471911ed8ce403810208b20c; __sdcfduid=bcd31ce1471911ed8ce403810208b20ca20f468570ee39f4c7e8816203c0430bacb68c4b3fb93c18f47b74eac65320b9; _gcl_au=1.1.2068837318.1678201231; locale=ru; _gid=GA1.2.1215662139.1678454779; _ga=GA1.1.403083595.1678201201; OptanonConsent=isIABGlobal=false&datestamp=Fri+Mar+10+2023+20%3A26%3A19+GMT%2B0700+(Indochina+Time)&version=6.33.0&hosts=&landingPath=https%3A%2F%2Fdiscord.com%2F&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1; _ga_Q149DFWHT7=GS1.1.1678454779.3.0.1678454791.0.0.0; __cfruid=883e3dc69f7063e29528e874cd28ef2ec530a1a4-1678467965' \
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
#   --data-raw '{"type":3,"nonce":"1083840138678632448","guild_id":null,"channel_id":"1069126859100524575","message_flags":0,"message_id":"1083838511947448451","application_id":"936929561302675456","session_id":"7687ebdc6846e1f686f02b14c4f150d1","data":{"component_type":2,"custom_id":"MJ::JOB::upsample::4::350fb24a-dd72-45f2-ade8-048379a2ed5a"}}' \
#   --compressed



# {
#     "type": 3,
#     "nonce": "1083840138678632448",
#     "guild_id": null,
#     "channel_id": "1069126859100524575",
#     "message_flags": 0,
#     "message_id": "1083838511947448451",
#     "application_id": "936929561302675456",
#     "session_id": "7687ebdc6846e1f686f02b14c4f150d1",
#     "data": {
#         "component_type": 2,
#         "custom_id": "MJ::JOB::upsample::4::350fb24a-dd72-45f2-ade8-048379a2ed5a"
#     }
# }