"""
Midjourney wrapper via Discord client
"""

import re
import time
import json
import asyncio
import requests
import threading

from libdev.cfg import cfg
import websocket


TOKEN = cfg('discord.token')
SESSION = cfg('discord.session')
CHANNEL = cfg('discord.channel')
APPLICATION = '936929561302675456'
VERSION = '1077969938624553050'
ID = '938956540159881230'


def send_command(data):
    payload = {
        "type": 2,
        "application_id": APPLICATION,
        "channel_id": CHANNEL,
        "session_id": SESSION,
        "data": {
            "version": VERSION,
            "id": ID,
            "name": "imagine",
            "type": 1,
            "options": [{
                "type": 3,
                "name": "prompt",
                "value": data,
            }],
            "application_command": {
                "id": ID,
                "application_id": APPLICATION,
                "version": VERSION,
                "default_permission": True,
                "default_member_permissions": None,
                "type": 1,
                "name": "imagine",
                "description": "Create images with Midjourney",
                "dm_permission": True,
                "options": [{
                    "type": 3,
                    "name": "prompt",
                    "description": "The prompt to imagine",
                    "required": True,
                }],
            },
            "attachments": [],
        },
    }
    return requests.post(
        'https://discord.com/api/v9/interactions',
        headers={'Authorization': TOKEN},
        json=payload,
    ).text

def press_button(message, data):
    payload = {
        "type": 3,
        "guild_id": None,
        "channel_id": CHANNEL,
        "message_flags": 0,
        "message_id": message,
        "application_id": APPLICATION,
        "session_id": "7687ebdc6846e1f686f02b14c4f150d1",
        "data": {
            "component_type": 2,
            "custom_id": data,
        }
    }
    return requests.post(
        'https://discord.com/api/v9/interactions',
        headers={'Authorization': TOKEN},
        json=payload,
    ).text

def send_json_request(ws, request):
    ws.send(json.dumps(request))

def recieve_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)

def heartbeat(interval, ws):
    while True:
        time.sleep(interval)
        heartbeatJSON = {
            'op': 1,
            'd': 'null',
        }
        send_json_request(ws, heartbeatJSON)

def main():
    title = input("Request: ")
    send_command(title)

    ws = websocket.WebSocket()
    ws.connect('wss://gateway.discord.gg/?v=6&encording=json')

    # Online
    event = recieve_json_response(ws)
    heartbeat_interval = event['d']['heartbeat_interval'] / 1000
    threading._start_new_thread(heartbeat, (heartbeat_interval, ws))

    # Start session
    payload = {
        'op': 2,
        'd': {
            'token': TOKEN,
            'properties': {
                '$os': 'windows',
                '$browser': 'chrome',
                '$device': 'pc',
            },
        },
    }
    send_json_request(ws, payload)

    # Receiving
    while True:
        try:
            event = recieve_json_response(ws)

            # Check event
            if (
                not event
                or event['t'] != 'MESSAGE_CREATE'
                or event['d']['author']['id'] != APPLICATION
                or "%)" in event['d']['content']
                or (
                    "(fast" not in event['d']['content']
                    and "(relax" not in event['d']['content']
                )
            ):
                continue

            # Check desired image
            req = re.sub(r'.*\*\*([^*]*)\*\*.*', r'\1', event['d']['content'])
            if req != title:
                continue

            # Upscale
            if "Upscaled" not in event['d']['content']:
                message = event['d']['id']
                buttons = event['d']['components'][0]['components']
                press_button(message, buttons[0]['custom_id'])
                # press_button(message, buttons[1]['custom_id'])
                # press_button(message, buttons[2]['custom_id'])
                # press_button(message, buttons[3]['custom_id'])
                continue

            # Result
            url = event['d']['attachments'][0]['url']
            print(f"{title}: {url}")  # Paste your code here
            break

        except:
            pass


if __name__ == '__main__':
    asyncio.run(main())
