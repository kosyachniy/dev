import requests

API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'https://chill.services/discord'

# def exchange_code(code):
#     data = {
#         'client_id': CLIENT_ID,
#         'client_secret': CLIENT_SECRET,
#         'grant_type': 'authorization_code',
#         'code': code,
#         'redirect_uri': REDIRECT_URI
#     }
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
#     r.raise_for_status()
#     return r.json()

def get_token():
    data = {
        'grant_type': 'client_credentials',
        'scope': 'identify connections'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
    r.raise_for_status()
    return r.json()


def exchange_code(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
    r.raise_for_status()
    return r.json()


if __name__ == '__main__':
    # exchange_code('')

    # token = get_token()
    # print(token)

    print(exchange_code(input("Code: ")))


# {'access_token': '', 'expires_in': 604800, 'scope': 'identify connections', 'token_type': 'Bearer'}

# {'access_token': '', 'expires_in': 604800, 'refresh_token': '', 'scope': 'connections guilds identify email', 'token_type': 'Bearer', 'webhook': {'type': 1, 'id': '1083767716898418803', 'name': 'chill', 'avatar': 'd9b4075d24ac26f6b563af1a4fdf32e0', 'channel_id': '1083764068562771968', 'guild_id': '667320783579774977', 'application_id': '1083747207385186424', 'token': '', 'url': 'https://discord.com/api/webhooks/1083767716898418803/'}}


# https://discord.com/api/webhooks/1083767716898418803/
# {"type": 1, "id": "1083767716898418803", "name": "chill", "avatar": "d9b4075d24ac26f6b563af1a4fdf32e0", "channel_id": "1083764068562771968", "guild_id": "667320783579774977", "application_id": "1083747207385186424", "token": ""}