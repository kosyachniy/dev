import bitly_api
import sys

# Define your API information

API_USER = "34dcf60dd0af202267b2e7315cd619f68a9d0fc3"
API_KEY = "e67905dc63f8811a43f487cfc81a2f3e01bc95a0"

b = bitlyapi.BitLy(API_USER, API_KEY)

# Define how to use the program

usage = """Usage: python shortener.py [url]
e.g python shortener.py http://www.google.com"""

if len(sys.argv) != 2:
    print(usage)
    sys.exit(0)

longurl = sys.argv[1]

response = b.shorten(longUrl=longurl)

print(response['url'])
